document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const previewImg = document.getElementById('preview-img');
    const resultsDiv = document.getElementById('results');
    const loading = document.getElementById('loading');

    // Drag & Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
        dropArea.addEventListener(event, e => e.preventDefault());
    });

    ['dragenter', 'dragover'].forEach(event => {
        dropArea.addEventListener(event, () => dropArea.classList.add('dragover'));
    });

    ['dragleave', 'drop'].forEach(event => {
        dropArea.addEventListener(event, () => dropArea.classList.remove('dragover'));
    });

    dropArea.addEventListener('drop', e => {
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) handleFile(file);
    });

    dropArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = e => {
            previewImg.src = e.target.result;
            preview.classList.remove('d-none');
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('file', file);

        loading.classList.remove('d-none');
        resultsDiv.classList.add('d-none');

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            loading.classList.add('d-none');
            showResults(data);
        })
        .catch(err => {
            loading.classList.add('d-none');
            resultsDiv.innerHTML = `<div class="alert alert-danger">Server Error: ${err.message}</div>`;
            resultsDiv.classList.remove('d-none');
        });
    }

    function showResults(data) {
        let html = `<div class="card result-card shadow-lg mb-4 ${data.classification.includes('TRUCK') ? 'status-truck' : 'status-notruck'}">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">
                    <i class="fas ${data.classification.includes('TRUCK') ? 'fa-check-circle text-success' : 'fa-times-circle text-danger'}"></i>
                    Classification: <strong>${data.classification}</strong>
                </h3>`;

        if (data.classification.includes('NOT')) {
            html += `<p class="text-center text-danger fs-5">Only trucks are processed for plate verification.</p></div></div>`;
        } else {
            html += `
                <div class="row text-center mb-4">
                    <div class="col-md-6">
                        <h5><i class="fas fa-license-plate text-primary"></i> Detected Plate</h5>
                        <h2 class="text-primary fw-bold">${data.plate || 'Not Detected'}</h2>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-database"></i> Database Status</h5>
                        <h4 class="${data.message.includes('Found') ? 'text-success' : 'text-warning'}">${data.message}</h4>
                    </div>
                </div>`;

            if (data.details) {
                html += `<div class="card bg-light border-0">
                    <div class="card-body">
                        <h4 class="text-success text-center mb-4"><i class="fas fa-car"></i> Vehicle Details Found</h4>
                        <div class="row g-4">
                            <div class="col-md-6"><strong>Registration No:</strong> ${data.details['Registration No'] || '-'}</div>
                            <div class="col-md-6"><strong>Maker:</strong> ${data.details.Maker || '-'}</div>
                            <div class="col-md-6"><strong>Model:</strong> ${data.details.Model || '-'}</div>
                            <div class="col-md-6"><strong>Fuel Type:</strong> ${data.details.Fuel || '-'}</div>
                            <div class="col-md-6"><strong>CC:</strong> ${data.details.CC || '-'} cc</div>
                            <div class="col-md-6"><strong>Seating:</strong> ${data.details['Seating Capacity'] || '-'} seats</div>
                            <div class="col-md-6"><strong>Valid From:</strong> ${data.details['Registration Valid From'] || '-'}</div>
                            <div class="col-md-6"><strong>Valid Till:</strong> ${data.details['Registration Valid To'] || '-'}</div>
                        </div>
                    </div>
                </div>`;
            }
            html += `</div></div>`;
        }

        resultsDiv.innerHTML = html;
        resultsDiv.classList.remove('d-none');
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }
});