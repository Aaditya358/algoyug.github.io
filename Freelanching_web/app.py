import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'freelancers.db'

# --- Database Functions ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Helper Function for Uploads ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('home.html', user_name=user['name'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        
        return "Invalid email or password. <a href='/login'>Try again</a>"
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullName = request.form['fullName']
        email = request.form['email']
        password = request.form['password']
        db = get_db()

        if db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            return f'Email {email} is already registered. <a href="/login">Login instead</a>'

        db.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (fullName, email, generate_password_hash(password))
        )
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form['fullName']
        skills = request.form['skills']
        db.execute(
            'UPDATE users SET name = ?, skills = ? WHERE id = ?',
            (name, skills, user_id)
        )
        db.commit()
        return redirect(url_for('home'))
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return render_template('profile.html', user=user)

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user_id = session['user_id']

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # To avoid overwrites, you might want to add a unique prefix to the filename
            # For example: filename = f"{user_id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save filename to the new portfolio_items table
            db.execute('INSERT INTO portfolio_items (user_id, filename) VALUES (?, ?)', (user_id, filename))
            db.commit()
            return redirect(url_for('portfolio'))

    # GET request: fetch and display uploaded files
    uploaded_files = db.execute('SELECT filename FROM portfolio_items WHERE user_id = ?', (user_id,)).fetchall()
    return render_template('portfolio.html', files=uploaded_files)

# New route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    questions = [{'text': 'What does HTML stand for?', 'options': ['Hyper Text Markup Language', 'High Text Markup Language', 'Hyper Tabular Markup Language'], 'answer': 'Hyper Text Markup Language'}, {'text': 'Which tag is used to create a hyperlink?', 'options': ['<link>', '<a>', '<href>'], 'answer': '<a>'}]
    if request.method == 'POST':
        score = 0
        for i, question in enumerate(questions):
            if request.form.get(f'q{i+1}') == question['answer']:
                score += 1
        return render_template('results.html', score=score, total=len(questions))
    return render_template('test.html', questions=questions)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)