const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const statusArea = document.getElementById('statusArea');
const filePreviewContainer = document.getElementById('filePreviewContainer');
const imagePreview = document.getElementById('imagePreview');
const docIcon = document.getElementById('docIcon');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const processBtn = document.getElementById('processBtn');
const removeFileBtn = document.getElementById('removeFileBtn');
const resultArea = document.getElementById('resultArea');
const resultPlaceholder = document.getElementById('resultPlaceholder');
const textContent = document.getElementById('textContent');
const loader = document.getElementById('loader');
const charCount = document.getElementById('charCount');
const insightsContainer = document.getElementById('insightsContainer');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');

const imageModal = document.getElementById('imageModal');
const modalImg = document.getElementById('modalImg');
const closeModal = document.getElementById('closeModal');

const insightPages = document.getElementById('insightPages');
const insightWords = document.getElementById('insightWords');
const insightType = document.getElementById('insightType');
const insightExt = document.getElementById('insightExt');
const insightTime = document.getElementById('insightTime');

let selectedFile = null;
let currentImgData = null;

const toggleProcessing = (isProcessing) => {
    processBtn.disabled = isProcessing;
    removeFileBtn.disabled = isProcessing;
    copyBtn.disabled = isProcessing;
    downloadBtn.disabled = isProcessing;
    fileInput.disabled = isProcessing;

    if (isProcessing) {
        loader.classList.remove('hidden');
        resultPlaceholder.classList.remove('hidden');
        resultArea.classList.add('hidden');
        insightsContainer.classList.add('hidden');
    } else {
        loader.classList.add('hidden');
    }
};

dropZone.onclick = () => {
    if (!processBtn.disabled) fileInput.click();
};
fileInput.onchange = (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
};
dropZone.ondragover = (e) => {
    e.preventDefault();
    if (!processBtn.disabled) dropZone.classList.add('active');
};
dropZone.ondragleave = () => dropZone.classList.remove('active');
dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove('active');
    if (!processBtn.disabled && e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
};

function handleFile(file) {
    selectedFile = file;
    fileName.innerText = file.name;
    fileSize.innerText = `${(file.size / 1024 / 1024).toFixed(2)} MB`;

    dropZone.classList.add('hidden');
    statusArea.classList.remove('hidden');

    resultArea.classList.add('hidden');
    resultPlaceholder.classList.remove('hidden');
    insightsContainer.classList.add('hidden');

    if (file.type.startsWith('image/')) {
        docIcon.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        const reader = new FileReader();
        reader.onload = (e) => {
            currentImgData = e.target.result;
            imagePreview.style.backgroundImage = `url(${e.target.result})`;
            hoverOverlay.classList.remove('hidden');
            const img = new Image();
            img.onload = () => {
                if (img.height > img.width) {
                    filePreviewContainer.classList.remove('min-h-[16rem]');
                    filePreviewContainer.classList.add('min-h-[28rem]');
                } else {
                    filePreviewContainer.classList.remove('min-h-[28rem]');
                    filePreviewContainer.classList.add('min-h-[16rem]');
                }
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    } else {
        currentImgData = null;
        imagePreview.classList.add('hidden');
        hoverOverlay.classList.add('hidden');
        docIcon.classList.remove('hidden');
        filePreviewContainer.classList.remove('min-h-[28rem]');
        filePreviewContainer.classList.add('min-h-[16rem]');
    }
}

// Modal Logic
filePreviewContainer.onclick = () => {
    if (currentImgData) {
        modalImg.src = currentImgData;
        imageModal.classList.remove('hidden');
        imageModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

const closeImageModal = () => {
    imageModal.classList.add('hidden');
    imageModal.classList.remove('active');
    document.body.style.overflow = 'auto';
};

closeModal.onclick = closeImageModal;
imageModal.onclick = (e) => {
    if (e.target === imageModal) closeImageModal();
};

const resetUploadState = () => {
    if (processBtn.disabled) return;
    selectedFile = null;
    currentImgData = null;
    fileInput.value = '';

    dropZone.classList.remove('hidden');
    statusArea.classList.add('hidden');

    resultArea.classList.add('hidden');
    insightsContainer.classList.add('hidden');
    resultPlaceholder.classList.remove('hidden');
    textContent.innerText = '';
};

removeFileBtn.onclick = resetUploadState;


async function fetchApiToken() {
    try {
        const res = await fetch("/api/token");
        if (!res.ok) throw new Error("Failed to fetch API token");
        const data = await res.json();
        return data.token;
    } catch (err) {
        console.error(err);
        alert("Could not get API token. Please try again.");
        return null;
    }
}


// Backend Integration
processBtn.onclick = async () => {
    if (!selectedFile || processBtn.disabled) {
        alert("Please select a file first.");
        return;
    }

    toggleProcessing(true);

    // Fetch the API token once
    let apiToken = await fetchApiToken();
    if (!apiToken) {
        toggleProcessing(false);
        return;
    }

    // Create FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('grayscale', document.getElementById('paramGrayscale').checked);
    formData.append('denoise', document.getElementById('paramDenoise').checked);
    formData.append('brightness', document.getElementById('paramBrightness').value);
    formData.append('contrast', document.getElementById('paramContrast').value);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                "X-Token": apiToken
            },
            body: formData
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            throw new Error(`Server returned invalid JSON: ${e.message}`);
        }

        if (!response.ok) {
            let message = 'Processing failed';
            if (result.detail) {
                if (Array.isArray(result.detail)) {
                    message = result.detail.map(d => d.msg).join(', ');
                } else if (typeof result.detail === 'string') {
                    message = result.detail;
                }
            }
            throw new Error(message);
        }

        const { content, insights } = result.data;

        // Content display
        textContent.innerText = content;
        charCount.innerText = `${content.length} characters`;

        // Update metrics
        insightPages.innerText = insights.page_count || '1';
        insightWords.innerText = insights.word_count?.toLocaleString() || '0';
        insightType.innerText = insights.type || 'N/A';
        insightExt.innerText = insights.extension || 'N/A';
        insightTime.innerText = insights.execution_time;

        resultArea.classList.remove('hidden');
        resultPlaceholder.classList.add('hidden');
        insightsContainer.classList.remove('hidden');

    } catch (err) {
        textContent.innerHTML = `<span class="text-red-400 font-bold">[ERROR]</span>\n${err.message}`;
        resultArea.classList.remove('hidden');
        resultPlaceholder.classList.add('hidden');
    } finally {
        toggleProcessing(false);
    }
};

copyBtn.onclick = () => {
    if (copyBtn.disabled) return;
    const text = textContent.innerText;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerText = "Copied!";
        setTimeout(() => copyBtn.innerHTML = originalText, 2000);
    });
};

// Download Logic
downloadBtn.onclick = () => {
    if (downloadBtn.disabled) return;
    const text = textContent.innerText;
    if (!text) return;

    const blob = new Blob([text], {
        type: 'text/plain'
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    const originalBaseName = selectedFile ? selectedFile.name.split('.')[0] : 'extracted_text';

    a.href = url;
    a.download = `${originalBaseName}_extracted.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};