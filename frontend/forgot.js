document.getElementById("forgotForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    const response = await fetch("http://127.0.0.1:5000/forgot-password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    message.style.display = "block";
message.textContent = data.message;

if (response.ok) {
    message.className = "success";
    setTimeout(() => {
        window.location.href = "login.html";
    }, 1500);
} else {
    message.className = "error";
}
});
