const uploadContainer = document.getElementById('upload-container');
const fileInput = document.getElementById('file-input');
const uploadedFilesList = document.getElementById('uploaded-files');
const loader = document.getElementById('loader');

// Drag-and-drop events
uploadContainer.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadContainer.classList.add('dragover');
});

uploadContainer.addEventListener('dragleave', () => {
    uploadContainer.classList.remove('dragover');
});

uploadContainer.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadContainer.classList.remove('dragover');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

// When user clicks to select files
uploadContainer.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    handleFiles(files);
});

// Handle files (show names and add to form)
function handleFiles(files) {
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('file', file);

        // Display uploaded file name immediately in the list
        const fileItem = document.createElement('li');
        fileItem.textContent = file.name;
        uploadedFilesList.appendChild(fileItem);
    });

    showLoader();
    submitForm(formData);
}

// Show loader
function showLoader() {
    loader.style.display = 'block';
}

// Hide loader
function hideLoader() {
    loader.style.display = 'none';
}

// Submit form
function submitForm(formData) {
    fetch('/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.success) {
            alert(data.success);
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        hideLoader();
        alert('An error occurred.');
    });
}
