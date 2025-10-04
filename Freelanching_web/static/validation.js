// This function will run when the registration form is submitted
document.addEventListener('DOMContentLoaded', () => {
    // Find the registration form by its ID
    const form = document.getElementById('registrationForm');

    form.addEventListener('submit', function(event) {
        // Get the password value
        const password = document.getElementById('password').value;

        // Check if the password is less than 8 characters
        if (password.length < 8) {
            // Prevent the form from submitting
            event.preventDefault(); 
            
            // Show an alert message
            alert('Password must be at least 8 characters long.');
        }
    });
});