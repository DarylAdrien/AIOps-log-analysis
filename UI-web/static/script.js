document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('logAnalysisForm');
    const statusMessage = document.getElementById('statusMessage');
    const resultsSection = document.getElementById('results');
    const anomaliesTableBody = document.querySelector('#anomaliesTable tbody'); // Select the tbody
    const noAnomaliesMessage = document.getElementById('noAnomaliesMessage');
    // const fullLogOutput = document.getElementById('fullLogOutput'); // Removed as it's no longer displayed

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        statusMessage.textContent = 'Analyzing logs and sending email... Please wait.';
        statusMessage.className = 'status-message info';
        resultsSection.style.display = 'none'; // Hide previous results
        anomaliesTableBody.innerHTML = ''; // Clear previous table rows
        noAnomaliesMessage.style.display = 'none'; // Hide no anomalies message

        const formData = new FormData(form); // Collect form data (file and email)

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                statusMessage.textContent = data.message;
                statusMessage.className = 'status-message success';

                // Display anomalies in a table
                if (data.anomalies && data.anomalies.length > 0) {
                    data.anomalies.forEach(anomaly => {
                        const row = anomaliesTableBody.insertRow(); // Insert a new row
                        const timestampCell = row.insertCell();
                        const levelCell = row.insertCell();
                        const messageCell = row.insertCell();

                        timestampCell.textContent = anomaly.timestamp;
                        levelCell.textContent = anomaly.level;
                        messageCell.textContent = anomaly.message;
                    });
                    anomaliesTableBody.style.display = 'table-row-group'; // Ensure tbody is visible
                    noAnomaliesMessage.style.display = 'none'; // Hide no anomalies message
                } else {
                    anomaliesTableBody.style.display = 'none'; // Hide table body
                    noAnomaliesMessage.style.display = 'block'; // Show no anomalies message
                }

                resultsSection.style.display = 'block'; // Show results section

            } else {
                statusMessage.textContent = `Error: ${data.message}`;
                statusMessage.className = 'status-message error';
                resultsSection.style.display = 'none';
            }
        } catch (error) {
            console.error('Fetch error:', error);
            statusMessage.textContent = `An unexpected error occurred: ${error.message}. Please try again.`;
            statusMessage.className = 'status-message error';
            resultsSection.style.display = 'none';
        }
    });
});