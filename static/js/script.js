document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded! 🚀");

    // Selecting elements
    const alertContainer = document.getElementById("alert-container");
    const fileInput = document.getElementById("file-upload");
    const fileNameDisplay = document.getElementById("file-name");
    const graphSelect = document.getElementById("graph-type");
    const generateButton = document.getElementById("generate-graph");

    // Function to show success/error messages
    function showMessage(message, type) {
        alertContainer.innerHTML = ""; // Clear previous messages
        const alertBox = document.createElement("div");
        alertBox.className = `alert ${type === "success" ? "bg-green-500" : "bg-red-500"} text-white p-2 rounded-md mt-2`;
        alertBox.textContent = message;
        alertContainer.appendChild(alertBox);

        // Remove message after 3 seconds
        setTimeout(() => {
            alertBox.remove();
        }, 3000);
    }

    // **Ensure login success messages don’t appear on the register page**
    if (window.location.pathname.includes("register")) {
        sessionStorage.removeItem("successMessage"); // ✅ Remove stored success message
        alertContainer.innerHTML = ""; // ✅ Clear any existing messages in the alert container
        console.log("Cleared session storage on register page!"); // Debugging log
    }

    // **Retrieve and display stored success messages (only if not on register page)**
    if (!window.location.pathname.includes("register")) {
        const storedMessage = sessionStorage.getItem("successMessage");
        if (storedMessage) {
            showMessage(storedMessage, "success");
            sessionStorage.removeItem("successMessage"); // Clear message after displaying
        }
    }

    // **Extra forceful fix** (remove all session storage when Register Page loads)
    window.addEventListener("load", function () {
        if (window.location.pathname.includes("register")) {
            sessionStorage.clear(); // 🚀 Fully clears session storage
            console.log("Session storage fully cleared on register page load!");
        }
    });

    // Update file label when a file is selected
    if (fileInput) {
        fileInput.addEventListener("change", function () {
            fileNameDisplay.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : "No file chosen";
        });
    }

    // Handle "Generate Graph" button click
    if (generateButton) {
        generateButton.addEventListener("click", function () {
            const selectedFile = fileInput.files.length > 0 ? fileInput.files[0] : null;
            const selectedGraph = graphSelect.value;

            if (!selectedFile) {
                showMessage("⚠️ Please upload a file before generating the graph.", "error");
                return;
            }

            if (!selectedGraph) {
                showMessage("⚠️ Please select a graph type before generating.", "error");
                return;
            }

            // Disable button to prevent multiple clicks
            generateButton.disabled = true;
            generateButton.textContent = "Processing...";

            // Send form data to backend using AJAX
            const formData = new FormData();
            formData.append("file", selectedFile);
            formData.append("graphType", selectedGraph);

            fetch("/upload", {
                method: "POST",
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server Response:", data);
                if (data.success) {
                    sessionStorage.setItem("successMessage", "✅ File uploaded and graph generated successfully!");
                    setTimeout(() => {
                        window.location.href = `/dashboard?graph=${selectedGraph}&file=${encodeURIComponent(selectedFile.name)}`;
                    }, 2000);
                } else {
                    showMessage("❌ Error generating graph. Try again.", "error");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showMessage("⚠️ Something went wrong. Check the console.", "error");
            })
            .finally(() => {
                generateButton.disabled = false;
                generateButton.textContent = "Generate Graph";
            });
        });
    }
});
