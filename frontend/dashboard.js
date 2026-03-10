// ================= API HELPER =================
const BASE_URL = "http://localhost:5000";

let lastCommand = "";

function apiRequest(endpoint, options = {}) {
    return fetch(`${BASE_URL}${endpoint}`, options)
        .then(res => {
            if (!res.ok) {
                return res.json().then(err => { throw err; });
            }
            return res.json();
        });
}

// ================= PAGE NAVIGATION =================
function showPage(pageId) {

    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    document.getElementById(pageId).classList.add('active');

    if (pageId === "history") loadEmailHistory();
    if (pageId === "home") loadDashboardStats();
}

// ================= UPLOAD AUDIO =================
function uploadAudio() {

    const fileInput = document.getElementById("voiceFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an audio file first");
        return;
    }

    const formData = new FormData();
    formData.append("audio", file);

    apiRequest("/upload-audio", {
        method: "POST",
        body: formData
    })
    .then(data => {

        document.getElementById("uploadMessage").style.display = "block";

        if (data.original_text && data.translated_text) {

            document.getElementById("voiceText").value =
                "Original: " + data.original_text + "\n" +
                "Translated: " + data.translated_text;
        }
    })
    .catch(err => {
        console.error("UPLOAD ERROR:", err);
    
        alert(
            err.details ||
            err.error ||
            "Audio upload failed — check backend console"
        );
    });    
}

// ================= VOICE → EMAIL =================
function convertVoiceToEmail() {

    const voiceCommand = document.getElementById("voiceText").value;

    if (!voiceCommand.trim()) {
        alert("Upload audio first");
        return;
    }

    generateEmailPreview(voiceCommand);

    apiRequest("/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: voiceCommand })
    })
    .then(data => {

        document.getElementById("emailSubject").innerText = data.subject;
        document.getElementById("emailPreview").value = data.email;

        document.getElementById("detailDate").innerText = data.date;
        document.getElementById("detailTime").innerText = data.time;
        document.getElementById("detailAgenda").innerText = data.agenda;
        document.getElementById("detailParticipants").innerText = data.participants;
        document.getElementById("detailPlatform").innerText = data.platform;

        showPage("email");
    })
    .catch(err => {
        console.error(err);
        alert("Backend error");
    });
}

// ================= TEXT → EMAIL =================
function generateEmailPreview(commandInput = null) {

    let command;

    if (commandInput) {
        command = commandInput;
    } else {
        command = document.getElementById("textCommand").value;
    }

    if (!command.trim()) {
        alert("Please enter a command");
        return;
    }

    // ⭐ save for regenerate
    lastCommand = command;

    apiRequest("/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
    })
    .then(data => {

        document.getElementById("emailSubject").innerText = data.subject;
        document.getElementById("emailPreview").value = data.email;

        document.getElementById("detailDate").innerText = data.date;
        document.getElementById("detailTime").innerText = data.time;
        document.getElementById("detailAgenda").innerText = data.agenda;
        document.getElementById("detailParticipants").innerText = data.participants;
        document.getElementById("detailPlatform").innerText = data.platform;

        showPage("email");
    })
    .catch(err => {
        console.error(err);
        alert("Backend error");
    });
}

// ================= SEND EMAIL =================
function sendEmail() {

    const subject = document.getElementById("emailSubject").innerText;
    const emailBody = document.getElementById("emailPreview").value;
    const recipients = document.getElementById("recipients").value;
    const attachmentFile = document.getElementById("attachment").files[0];

    if (!recipients.trim()) {
        alert("Enter recipient emails");
        return;
    }

    const formData = new FormData();
    formData.append("user_email", localStorage.getItem("userEmail"));
    formData.append("subject", subject);
    formData.append("email", emailBody);
    formData.append("recipients", recipients);

    if (attachmentFile) {
        formData.append("attachment", attachmentFile);
    }

    fetch(`${BASE_URL}/send-email`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        loadDashboardStats();
    })
    .catch(() => alert("Error sending email"));
}

// ================= LOAD EMAIL HISTORY =================
function loadEmailHistory() {

    const userEmail = localStorage.getItem("userEmail");

    if (!userEmail) {
        alert("User not logged in");
        return;
    }

    apiRequest(`/email-history?email=${userEmail}`)
    .then(data => {

        const table = document.getElementById("historyTable");

        table.innerHTML = `
            <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Subject</th>
                <th>Status</th>
            </tr>
        `;

        if (data.length === 0) {
            const row = table.insertRow();
            row.innerHTML = `<td colspan="4">No emails found</td>`;
            return;
        }

        data.forEach(item => {

            const row = table.insertRow();
            const parts = item.sent_at.split(" ");

            row.insertCell(0).innerText = parts[0];
            row.insertCell(1).innerText = parts.slice(1).join(" ");            
            row.insertCell(2).innerText = item.subject;

            const statusCell = row.insertCell(3);
            statusCell.innerText = item.status;

            statusCell.style.color =
                item.status === "SENT" ? "green" : "red";

            statusCell.style.fontWeight = "bold";
        });
    })
    .catch(err => {
        console.error(err);
        alert("Failed to load history");
    });
}

// ================= DASHBOARD STATS =================
function loadDashboardStats() {

    const userEmail = localStorage.getItem("userEmail");
    if (!userEmail) return;

    apiRequest(`/dashboard-stats?email=${userEmail}`)
    .then(data => {

        document.getElementById("totalEmails").innerText = data.total_emails;
        document.getElementById("todayEmails").innerText = data.emails_today;
        document.getElementById("lastEmail").innerText = data.last_email;
    })
    .catch(err => console.error("Stats error:", err));
}

// ================= LOGOUT MODAL =================
function openLogout() {
    document.getElementById("confirmationModal").style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

// ================= INIT =================
window.onload = () => {
    loadDashboardStats();
};


function regenerateEmail() {

    if (!lastCommand) {
        alert("Nothing to regenerate");
        return;
    }

    generateEmailPreview(lastCommand);
}
