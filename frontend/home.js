// Navigation Button Actions
document.addEventListener("DOMContentLoaded", () => {

    // Login button
    const loginLinks = document.querySelectorAll('a[href="login.html"]');
    loginLinks.forEach(link => {
        link.addEventListener("click", () => {
            console.log("Redirecting to Login page");
        });
    });

    // Signup button
    const signupLinks = document.querySelectorAll('a[href="signup.html"]');
    signupLinks.forEach(link => {
        link.addEventListener("click", () => {
            console.log("Redirecting to Signup page");
        });
    });
});

// Smooth Scroll for Navbar Links
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', e => {
        if (link.getAttribute('href').startsWith('#')) {
            e.preventDefault();
            document.querySelector(link.getAttribute('href'))
                .scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Feature Click Info
document.querySelectorAll('.feature-box').forEach(feature => {
    feature.addEventListener('click', () => {
        alert("Selected Feature:\n" + feature.innerText);
    });
});
console.log("Modern Home Page Loaded");

// Page Load Message (Optional)
window.onload = () => {
    console.log("Meeting Email Auto Generator - Home Page Loaded");
};

// Scroll animation
const animatedElements = document.querySelectorAll('.animate');

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        }
    });
}, { threshold: 0.2 });
animatedElements.forEach(el => observer.observe(el));

// Feature click info
document.querySelectorAll('.feature-box').forEach(box => {
    box.addEventListener('click', () => {
        alert("Feature Selected:\n" + box.innerText);
    });
});
console.log("MEAG Single Page Loaded Successfully");