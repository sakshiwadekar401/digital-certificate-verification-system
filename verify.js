document.getElementById('verifyButton').addEventListener('click', function() {
    const fileInput = document.getElementById('certificateInput');
    const resultDiv = document.getElementById('verificationResult');
    const downloadLink = document.getElementById('downloadLink'); // Add download link element

    if (fileInput.files.length === 0) {
        resultDiv.textContent = 'Please select a certificate file.';
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('certificate', file);

    fetch('/verify_certificate', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Certificate Verified' && data.fileUrl) { // Check for fileUrl
            resultDiv.textContent = 'Verification Successful!';
            resultDiv.style.color = 'green';

            // Display download link
            downloadLink.href = data.fileUrl;
            downloadLink.style.display = 'block'; // Show the link

        } else if (data.message === 'Certificate Not Verified') {
            resultDiv.textContent = 'Verification Failed.';
            resultDiv.style.color = 'red';
            downloadLink.style.display = 'none'; // hide the download link.
        } else if (data.message === 'Certificate Not Found on Blockchain') {
            resultDiv.textContent = 'Certificate Not Found on Blockchain.';
            resultDiv.style.color = 'orange';
            downloadLink.style.display = 'none'; // hide the download link.
        } else if(data.error){
            resultDiv.textContent = 'Error: ' + data.error;
            resultDiv.style.color = 'red';
            downloadLink.style.display = 'none'; // hide the download link.
        } else {
            resultDiv.textContent = 'Unexpected Error.';
            resultDiv.style.color = 'red';
            downloadLink.style.display = 'none'; // hide the download link.
        }
    })
    .catch(error => {
        resultDiv.textContent = 'Network error: ' + error;
        resultDiv.style.color = 'red';
        downloadLink.style.display = 'none'; // hide the download link.
    });
});

// Add a download link element to your HTML:
 <a id="downloadLink" href="#" style="display: none;" download="certificate.pdf">Download Certificate</a>