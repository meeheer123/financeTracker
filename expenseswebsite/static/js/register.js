const usernameField = document.getElementById('usernameField');
const feedbackArea = document.querySelector('.invalid-feedback');
const emailField = document.getElementById('emailField');
const emailFeedbackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const emailSuccessOutput = document.querySelector('.emailSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submit-btn');

// Track validation states
let isUsernameValid = false;
let isEmailValid = false;

// Debounce function
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

showPasswordToggle.addEventListener('click', (e) => {
    if (showPasswordToggle.textContent === 'SHOW') {
        showPasswordToggle.textContent = 'HIDE';
        passwordField.setAttribute('type', 'text');
    } else {
        showPasswordToggle.textContent = 'SHOW';
        passwordField.setAttribute('type', 'password');
    }
});

const validateEmail = (e) => {
    const emailVal = e.target.value;

    emailField.classList.remove("is-invalid");
    emailFeedbackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/authentication/validate-email/", {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.email_error) {
                isEmailValid = false;
                emailField.classList.add("is-invalid");
                emailFeedbackArea.style.display = "block";
                emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                isEmailValid = true;
                emailField.classList.remove("is-invalid");
                emailField.classList.add("is-valid");
                emailFeedbackArea.style.display = "none";
            }
            toggleSubmitButton();  // Check if the submit button should be enabled/disabled
        });
    }
};

const validateUsername = (e) => {
    const usernameVar = e.target.value;

    usernameSuccessOutput.style.display = 'block';
    usernameSuccessOutput.textContent = `Checking ${usernameVar}`;

    usernameField.classList.remove('is-invalid');
    feedbackArea.style.display = 'none';

    if (usernameVar.length > 0) {
        fetch('/authentication/validate-username/', {
            body: JSON.stringify({ username: usernameVar }),
            method: 'POST',
        })
        .then((res) => res.json())
        .then((data) => {
            usernameSuccessOutput.style.display = 'none';
            if (data.username_error) {
                isUsernameValid = false;
                usernameField.classList.add('is-invalid');
                feedbackArea.style.display = 'block';
                feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
            } else {
                isUsernameValid = true;
                usernameField.classList.remove('is-invalid');
                usernameField.classList.add('is-valid');
                feedbackArea.style.display = 'none';
            }
            toggleSubmitButton();  // Check if the submit button should be enabled/disabled
        });
    }
};

// Enable or disable the submit button based on validation states
function toggleSubmitButton() {
    if (isUsernameValid && isEmailValid) {
        submitBtn.removeAttribute('disabled');
    } else {
        submitBtn.disabled = true;
    }
}

emailField.addEventListener("keyup", debounce(validateEmail, 300));  // Debounce for email
usernameField.addEventListener('keyup', debounce(validateUsername, 300));  // Debounce for username
