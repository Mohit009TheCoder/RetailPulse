// Forecasting page JavaScript

let forecastChart = null;
let historicalData = [];
let forecastData = {};

// Load initial data
async function loadForecastingData() {
    try {
        showNotification('Loading historical data...', 'info');
        
        // Load historical data
        const histData = await apiCall('/api/forecast/historical');
        historicalData = histData.data;
        updateHistoricalStats(histData.stats);
        
        // Load top products
        const productsData = await apiCall('/api/forecast/products?limit=20');
        populateProductsTable(productsData.data);
        
        // Create initial historical chart
        createHistoricalChart();
        
        showNotification('Data loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading forecasting data:', error);
        showNotification('Error loading data', 'error');
    }
}

// Create historical chart
function createHistoricalChart() {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    // Show last 60 days of historical data for cleaner view
    const historicalSlice = historicalData.slice(-60);
    const dates = historicalSlice.map(d => d.Date);
    const quantities = historicalSlice.map(d => d.Total_Quantity);
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Historical Sales',
                data: quantities,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 13,
                            family: 'Inter',
                            weight: '500'
                        },
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 13,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            return 'Sales: ' + formatNumber(Math.round(context.parsed.y)) + ' units';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantity (units)',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
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
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 15
                    }
                }
            }
        }
    });
}

// Update historical statistics
function updateHistoricalStats(stats) {
    document.getElementById('avg-daily-revenue').textContent = formatCurrency(stats.avg_daily_revenue);
    document.getElementById('avg-daily-quantity').textContent = formatNumber(Math.round(stats.avg_daily_quantity));
    document.getElementById('avg-daily-orders').textContent = formatNumber(Math.round(stats.avg_daily_orders));
    document.getElementById('total-days').textContent = formatNumber(stats.total_days);
}

// Generate forecast
async function generateForecast() {
    try {
        const periods = parseInt(document.getElementById('forecastPeriods').value);
        
        showNotification('Generating forecasts...', 'info');
        
        const response = await apiCall('/api/forecast/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ periods })
        });
        
        forecastData = response.forecasts;
        
        // Update chart
        createForecastChart(periods);
        
        // Update table
        populateForecastTable(response.summary);
        
        showNotification('Forecasts generated successfully', 'success');
    } catch (error) {
        console.error('Error generating forecast:', error);
    }
}

// Create forecast chart
function createForecastChart(periods) {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    // Prepare historical data (last 60 days for cleaner view)
    const historicalSlice = historicalData.slice(-60);
    const historicalDates = historicalSlice.map(d => d.Date);
    const historicalValues = historicalSlice.map(d => d.Total_Quantity);
    
    // Prepare ensemble forecast (main forecast to show)
    const ensembleForecast = forecastData.ensemble || [];
    const forecastDates = ensembleForecast.map(d => d.Date);
    const forecastValues = ensembleForecast.map(d => d.Forecast_Quantity);
    
    // Combine dates
    const allDates = [...historicalDates, ...forecastDates];
    
    // Create datasets - only show Historical and Ensemble
    const datasets = [
        {
            label: 'Historical Sales',
            data: [...historicalValues, ...Array(forecastDates.length).fill(null)],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 4
        },
        {
            label: 'Ensemble Forecast (Recommended)',
            data: [...Array(historicalDates.length).fill(null), ...forecastValues],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6
        }
    ];
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 13,
                            family: 'Inter',
                            weight: '500'
                        },
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 13,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += formatNumber(Math.round(context.parsed.y)) + ' units';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantity (units)',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
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
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        maxTicksLimit: 15
                    }
                }
            }
        }
    });
}

// Populate forecast table
function populateForecastTable(summary) {
    const tbody = document.getElementById('forecastTableBody');
    tbody.innerHTML = '';
    
    summary.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${row.Method}</strong></td>
            <td>${formatNumber(Math.round(row.Avg_Daily_Forecast))} units</td>
            <td>${formatNumber(Math.round(row.Total_Forecast))} units</td>
            <td>${formatNumber(Math.round(row.Min_Forecast))} units</td>
            <td>${formatNumber(Math.round(row.Max_Forecast))} units</td>
        `;
        tbody.appendChild(tr);
    });
}

// Populate products table
function populateProductsTable(products) {
    const tbody = document.getElementById('productsTableBody');
    tbody.innerHTML = '';
    
    products.forEach((product, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${index + 1}</strong></td>
            <td>${product.Product}</td>
            <td>${formatNumber(product.Total_Quantity)}</td>
            <td>${formatCurrency(product.Total_Revenue)}</td>
            <td>${formatNumber(product.Total_Orders)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Show accuracy modal
async function showAccuracy() {
    try {
        const modal = document.getElementById('accuracyModal');
        modal.style.display = 'flex';
        
        const response = await apiCall('/api/forecast/accuracy?test_size=30');
        
        const tbody = document.getElementById('accuracyTableBody');
        tbody.innerHTML = '';
        
        response.data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${row.Method}</strong></td>
                <td>${row.MAE.toFixed(2)}</td>
                <td>${row.RMSE.toFixed(2)}</td>
                <td>${row.MAPE.toFixed(2)}%</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading accuracy metrics:', error);
        showNotification('Error loading accuracy metrics', 'error');
    }
}

// Close accuracy modal
function closeAccuracyModal() {
    const modal = document.getElementById('accuracyModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('accuracyModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', loadForecastingData);
