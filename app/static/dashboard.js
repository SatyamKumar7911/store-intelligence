const STORE_ID = "STORE_BLR_002";

async function fetchMetrics() {
    try {
        const response = await fetch(`/stores/${STORE_ID}/metrics`);
        const data = await response.json();
        
        document.getElementById('val-visitors').innerText = data.unique_visitors;
        document.getElementById('val-conversion').innerText = data.conversion_rate + "%";
        
        const queueElem = document.getElementById('val-queue');
        queueElem.innerText = data.queue_depth;
        if (data.queue_depth > 5) {
            queueElem.classList.add('danger');
        } else {
            queueElem.classList.remove('danger');
        }
        
        document.getElementById('val-abandon').innerText = data.abandonment_rate + "%";
        
    } catch (e) {
        console.error("Failed to fetch metrics", e);
    }
}

async function fetchAnomalies() {
    try {
        const response = await fetch(`/stores/${STORE_ID}/anomalies`);
        const data = await response.json();
        const alertBox = document.getElementById('anomaly-alert');
        
        if (data.anomalies && data.anomalies.length > 0) {
            alertBox.style.display = 'block';
            alertBox.innerHTML = `<strong>Anomaly Detected!</strong> ${data.anomalies[0].description} - <em>${data.anomalies[0].suggested_action}</em>`;
        } else {
            alertBox.style.display = 'none';
        }
    } catch (e) {
        console.error("Failed to fetch anomalies", e);
    }
}

// Poll every 3 seconds
setInterval(() => {
    fetchMetrics();
    fetchAnomalies();
}, 3000);

// Initial fetch
fetchMetrics();
fetchAnomalies();
