document.getElementById("signupForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirmPassword").value;
    if (password !== confirm) {
        alert("Passwords do not match");
        return;
    }

    const response = await fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();
    const messageBox = document.getElementById("message");

messageBox.style.display = "block";
messageBox.textContent = data.message;

if (response.ok) {
    messageBox.className = "success";

    setTimeout(() => {
        window.location.href = "login.html";
    }, 1500);
} else {
    messageBox.className = "error";
}

});
