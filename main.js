function processInstructions() {
    const instructions = document.getElementById('instructions').value;
    const button = document.querySelector('button');
    const dagImage = document.getElementById('dag-image');
    const sequenceList = document.getElementById('sequence-list');
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Processing...';
    dagImage.innerHTML = '<p>Generating DAG...</p>';
    sequenceList.innerHTML = '<p>Calculating sequence...</p>';
    
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ instructions: instructions })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display DAG image
        dagImage.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="DAG Visualization">`;
        
        // Display sequence
        sequenceList.innerHTML = data.sequence.map((labels, index) => 
            `${index + 1}. ${labels.join(', ')}`
        ).join('\n');
    })
    .catch(error => {
        console.error('Error:', error);
        dagImage.innerHTML = `<p class="error">Error: ${error.message || 'An error occurred while processing the instructions.'}</p>`;
        sequenceList.innerHTML = '<p class="error">Error occurred while calculating sequence.</p>';
    })
    .finally(() => {
        // Reset button state
        button.disabled = false;
        button.textContent = 'Generate DAG';
    });
} 