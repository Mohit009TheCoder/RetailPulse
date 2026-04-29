// Segments page JavaScript

// Load segments data
async function loadSegments() {
    try {
        const summaryData = await apiCall('/api/segment-summary');
        updateSegmentCards(summaryData.data);
        showNotification('Segments loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading segments:', error);
    }
}

// Update segment cards
function updateSegmentCards(data) {
    data.forEach(segment => {
        const segmentName = segment.Segment;
        const segmentKey = getSegmentKey(segmentName);
        
        // Update badge
        const badge = document.getElementById(`${segmentKey}-badge`);
        if (badge) {
            badge.textContent = formatNumber(segment['Customer Count']);
        }
        
        // Update stats
        const recency = document.getElementById(`${segmentKey}-recency`);
        if (recency) {
            recency.textContent = `${segment['Avg Recency'].toFixed(1)} days`;
        }
        
        const frequency = document.getElementById(`${segmentKey}-frequency`);
        if (frequency) {
            frequency.textContent = segment['Avg Frequency'].toFixed(1);
        }
        
        const monetary = document.getElementById(`${segmentKey}-monetary`);
        if (monetary) {
            monetary.textContent = formatCurrency(segment['Avg Monetary']);
        }
    });
}

// Get segment key for element IDs
function getSegmentKey(segmentName) {
    const keyMap = {
        'Champions': 'champions',
        'Loyal Customers': 'loyal',
        'Potential Loyalists': 'potential',
        'New Customers': 'new',
        'Promising': 'promising',
        'Need Attention': 'attention',
        'At Risk': 'risk',
        "Can't Lose Them": 'cantlose',
        'Hibernating': 'hibernating'
    };
    return keyMap[segmentName] || segmentName.toLowerCase().replace(/\s+/g, '-');
}

// View customers in a segment
function viewSegmentCustomers(segment) {
    window.location.href = `/customers?segment=${encodeURIComponent(segment)}`;
}

// Initialize segments page
document.addEventListener('DOMContentLoaded', loadSegments);
