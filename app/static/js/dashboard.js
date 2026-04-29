// Dashboard page JavaScript

let segmentChart = null;
let segmentBarChart = null;

// Load dashboard data
async function loadDashboard() {
    try {
        // Load segment summary
        const summaryData = await apiCall('/api/segment-summary');
        updateStats(summaryData.data);
        populateTable(summaryData.data);
        
        // Load segment distribution
        const distributionData = await apiCall('/api/segment-distribution');
        createCharts(distributionData.data);
        
        showNotification('Dashboard loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update statistics cards
function updateStats(data) {
    const totalCustomers = data.reduce((sum, item) => sum + item['Customer Count'], 0);
    const totalSegments = data.length;
    const avgMonetary = data.reduce((sum, item) => sum + (item['Avg Monetary'] * item['Customer Count']), 0) / totalCustomers;
    const championsCount = data.find(item => item.Segment === 'Champions')?.['Customer Count'] || 0;
    
    document.getElementById('total-customers').textContent = formatNumber(totalCustomers);
    document.getElementById('total-segments').textContent = totalSegments;
    document.getElementById('avg-monetary').textContent = formatCurrency(avgMonetary);
    document.getElementById('champions-count').textContent = formatNumber(championsCount);
}

// Populate segment table
function populateTable(data) {
    const tbody = document.getElementById('segmentTableBody');
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <span style="display: inline-block; width: 4px; height: 20px; background: ${getSegmentColor(row.Segment)}; margin-right: 8px; border-radius: 2px;"></span>
                <strong>${row.Segment}</strong>
            </td>
            <td>${formatNumber(row['Customer Count'])}</td>
            <td>${row['Avg Recency'].toFixed(1)} days</td>
            <td>${row['Avg Frequency'].toFixed(1)}</td>
            <td>${formatCurrency(row['Avg Monetary'])}</td>
            <td><span style="background: ${getSegmentColor(row.Segment)}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem; font-weight: 600;">${row['Avg RFM Score'].toFixed(1)}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

// Create charts
function createCharts(distributionData) {
    const labels = Object.keys(distributionData);
    const values = Object.values(distributionData);
    const colors = labels.map(label => getSegmentColor(label));
    
    // Pie Chart
    const pieCtx = document.getElementById('segmentChart').getContext('2d');
    if (segmentChart) segmentChart.destroy();
    
    segmentChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${formatNumber(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Bar Chart
    const barCtx = document.getElementById('segmentBarChart').getContext('2d');
    if (segmentBarChart) segmentBarChart.destroy();
    
    segmentBarChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Customer Count',
                data: values,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Customers: ${formatNumber(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    },
                    grid: {
                        color: '#e5e7eb'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Refresh data
async function refreshData() {
    showNotification('Refreshing data...', 'info');
    await loadDashboard();
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);
