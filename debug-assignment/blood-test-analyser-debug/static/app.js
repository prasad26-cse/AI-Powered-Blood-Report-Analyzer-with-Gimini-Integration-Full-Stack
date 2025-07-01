document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('file');
    const queryInput = document.getElementById('query');
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = 'Analyzing...';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('query', queryInput.value);

    try {
        const response = await fetch('/api/analyze-report-sync', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error('Server error: ' + response.status);
        }
        const data = await response.json();
        resultDiv.textContent = data.analysis || JSON.stringify(data);
    } catch (err) {
        resultDiv.textContent = 'Error: ' + err.message;
    }
}); 