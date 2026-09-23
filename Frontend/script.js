// ============================================================
// MergePDF - Frontend JavaScript
// ============================================================

// Store selected PDF files
let selectedFiles = [];


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const fileInput = document.getElementById("pdfFiles");
const fileList = document.getElementById("fileList");
const mergeBtn = document.getElementById("mergeBtn");
const status = document.getElementById("status");
const downloadLink = document.getElementById("downloadLink");
const downloadBtn = document.getElementById("downloadBtn");


// ============================================================
// SELECT PDF FILES
// ============================================================

fileInput.addEventListener("change", function () {

    const files = Array.from(fileInput.files);

    files.forEach(function (file) {

        // Check whether the file is PDF
        if (
            file.type === "application/pdf" ||
            file.name.toLowerCase().endsWith(".pdf")
        ) {

            // Prevent duplicate files
            const alreadyExists = selectedFiles.some(function (existingFile) {
                return (
                    existingFile.name === file.name &&
                    existingFile.size === file.size
                );
            });

            if (!alreadyExists) {
                selectedFiles.push(file);
            }

        } else {

            status.style.color = "red";
            status.textContent =
                file.name + " is not a PDF file.";

        }

    });

    // Display selected files
    displayFiles();

    // Clear input so the same file can be selected again
    fileInput.value = "";

});


// ============================================================
// DISPLAY SELECTED FILES
// ============================================================

function displayFiles() {

    // Clear previous list
    fileList.innerHTML = "";

    selectedFiles.forEach(function (file, index) {

        const listItem = document.createElement("li");

        listItem.className = "file-item";

        listItem.innerHTML = `
            <span class="file-name">
                ${index + 1}. ${file.name}
            </span>

            <button
                type="button"
                class="remove-btn"
                onclick="removeFile(${index})">
                Remove
            </button>
        `;

        fileList.appendChild(listItem);

    });


    // Enable merge button only when 2 or more PDFs are selected
    if (selectedFiles.length >= 2) {

        mergeBtn.disabled = false;

    } else {

        mergeBtn.disabled = true;

    }

}


// ============================================================
// REMOVE PDF FILE
// ============================================================

function removeFile(index) {

    if (index >= 0 && index < selectedFiles.length) {

        selectedFiles.splice(index, 1);

    }

    displayFiles();

    // Hide download button after changing files
    downloadLink.style.display = "none";

    status.textContent = "";

}


// ============================================================
// MERGE PDF FILES
// ============================================================

async function mergePDFs() {

    // Check minimum number of files
    if (selectedFiles.length < 2) {

        status.style.color = "red";

        status.textContent =
            "Please select at least 2 PDF files.";

        return;

    }


    // Create FormData
    const formData = new FormData();


    // Add all selected PDF files
    selectedFiles.forEach(function (file) {

        formData.append("files", file);

    });


    // Disable button while processing
    mergeBtn.disabled = true;

    mergeBtn.textContent = "Merging...";


    // Show status
    status.style.color = "#007bff";

    status.textContent =
        "Please wait, your PDFs are being merged...";


    // Hide previous download button
    downloadLink.style.display = "none";


    try {

        // Send files to FastAPI backend
        const response = await fetch("/merge", {

            method: "POST",

            body: formData

        });


        // Check server response
        if (!response.ok) {

            let errorMessage = "Failed to merge PDF files.";

            try {

                const errorData = await response.json();

                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }

            } catch (error) {

                // Response was not JSON
                console.log("Error response is not JSON.");

            }

            throw new Error(errorMessage);

        }


        // Convert response to PDF Blob
        const blob = await response.blob();


        // Create temporary download URL
        const url = window.URL.createObjectURL(blob);


        // Set download link
        downloadBtn.href = url;

        downloadBtn.download = "merged.pdf";


        // Show download button
        downloadLink.style.display = "block";


        // Success message
        status.style.color = "green";

        status.textContent =
            "PDFs merged successfully!";


    } catch (error) {

        console.error("Merge Error:", error);


        status.style.color = "red";

        status.textContent =
            error.message ||
            "Something went wrong while merging PDFs.";

    }


    // Enable button again
    mergeBtn.disabled = false;

    mergeBtn.textContent = "Merge PDFs";

}


// ============================================================
// CLEAN OBJECT URL AFTER DOWNLOAD
// ============================================================

downloadBtn.addEventListener("click", function () {

    setTimeout(function () {

        const url = downloadBtn.href;

        if (url.startsWith("blob:")) {

            window.URL.revokeObjectURL(url);

        }

    }, 1000);

});
