document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    // 1️⃣ Get input values
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const messageBox = document.getElementById("message");
    messageBox.style.display = "block";
    messageBox.textContent = "Logging in...";
    messageBox.className = "";

    try {
        // 2️⃣ Call backend login API
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        // 3️⃣ Parse response
        const data = await response.json();

        // 4️⃣ If login successful
        if (response.ok) {
            messageBox.textContent = data.message;
            messageBox.className = "success";

            // ⭐ VERY IMPORTANT (SAVE USER EMAIL)
            localStorage.setItem("userEmail", data.user.email);
            localStorage.setItem("userName", data.user.name);

            // ✅ Debug check (optional)
            console.log("Stored Email:", localStorage.getItem("userEmail"));

            // 5️⃣ Redirect to dashboard
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 1500);

        } else {
            // 6️⃣ Login failed
            messageBox.textContent = data.message || "Login failed";
            messageBox.className = "error";
        }

    } catch (error) {
        // 7️⃣ Network / server error
        console.error("Login error:", error);
        messageBox.textContent = "Server error. Try again later.";
        messageBox.className = "error";
    }
});