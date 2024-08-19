const usernameField = document.getElementById('usernameField');
const feedbackArea = document.querySelector('.invalid-feedback');
const emailField = document.getElementById('emailField');
const emailFeedbackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const emailSuccessOutput = document.querySelector('.emailSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submit-btn');

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
            console.log("data", data);
            if (data.email_error) {
                submitBtn.disabled = true;
                emailField.classList.add("is-invalid");
                emailFeedbackArea.style.display = "block";
                emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                submitBtn.removeAttribute('disabled');
            }
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
                submitBtn.disabled = true;
                usernameField.classList.add('is-invalid');
                feedbackArea.style.display = 'block';
                feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
            } else {
                submitBtn.removeAttribute('disabled');
            }
        });
    }
};

emailField.addEventListener("keyup", debounce(validateEmail, 300));  // Debounce for email
usernameField.addEventListener('keyup', debounce(validateUsername, 300));  // Debounce for username
