// Advanced Forecasting JavaScript

let advancedForecastChart = null;
let currentForecastData = null;
let dailyForecastData = null;
let historicalData = [];

// Load initial historical data
async function loadInitialData() {
    try {
        showNotification('Loading historical data...', 'info');
        
        // Load historical data
        const histData = await apiCall('/api/forecast/historical');
        historicalData = histData.data;
        
        // Create initial historical chart
        createHistoricalOnlyChart();
        
        showNotification('Ready! Click "Generate AI Forecast" to start.', 'success');
    } catch (error) {
        console.error('Error loading initial data:', error);
        showNotification('Error loading data', 'error');
    }
}

// Create chart with historical data only
function createHistoricalOnlyChart() {
    const ctx = document.getElementById('advancedForecastChart').getContext('2d');
    
    if (advancedForecastChart) {
        advancedForecastChart.destroy();
    }
    
    // Show last 60 days for cleaner view
    const historicalSlice = historicalData.slice(-60);
    const dates = historicalSlice.map(d => d.Date);
    const quantities = historicalSlice.map(d => d.Total_Quantity);
    
    advancedForecastChart = new Chart(ctx, {
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
    
    // Show the chart card
    document.getElementById('forecastChartCard').style.display = 'block';
}

// Generate advanced forecast
async function generateAdvancedForecast() {
    try {
        const periods = parseInt(document.getElementById('advancedForecastPeriods').value);
        
        showNotification('Generating AI-powered forecast...', 'info');
        
        const response = await apiCall('/api/advanced-forecast/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ periods })
        });
        
        currentForecastData = response;
        dailyForecastData = response.daily_forecast;
        
        // Update UI
        updateForecastSummary(response.summary);
        displayRecommendations(response.summary.recommendations);
        createAdvancedForecastChart(response.forecast);
        loadInventoryRecommendations();
        populateDailyForecastTable(response.daily_forecast);
        
        // Show all sections
        document.getElementById('forecastSummary').style.display = 'grid';
        document.getElementById('recommendationsSection').style.display = 'block';
        document.getElementById('forecastChartCard').style.display = 'block';
        document.getElementById('inventoryCard').style.display = 'block';
        document.getElementById('dailyForecastCard').style.display = 'block';
        
        showNotification('AI forecast generated successfully!', 'success');
    } catch (error) {
        console.error('Error generating forecast:', error);
    }
}

// Update forecast summary
function updateForecastSummary(summary) {
    document.getElementById('avgDailyForecast').textContent = formatNumber(Math.round(summary.avg_daily_forecast)) + ' units';
    
    const trendElement = document.getElementById('trendDirection');
    if (summary.trend_direction === 'increasing') {
        trendElement.textContent = '📈 Increasing';
        trendElement.style.color = '#10b981';
    } else {
        trendElement.textContent = '📉 Decreasing';
        trendElement.style.color = '#ef4444';
    }
    
    document.getElementById('totalForecast').textContent = formatNumber(Math.round(summary.total_forecast)) + ' units';
    document.getElementById('confidenceRange').textContent = '±' + formatNumber(Math.round(summary.confidence_range)) + ' units';
}

// Display recommendations
function displayRecommendations(recommendations) {
    const grid = document.getElementById('recommendationsGrid');
    grid.innerHTML = '';
    
    const priorityColors = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#3b82f6'
    };
    
    const typeIcons = {
        'growth': '📈',
        'decline': '📉',
        'stable': '➡️',
        'volatility': '📊',
        'scheduling': '📅',
        'uncertainty': '❓'
    };
    
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.style.borderLeftColor = priorityColors[rec.priority];
        
        card.innerHTML = `
            <div class="rec-header">
                <span class="rec-icon">${typeIcons[rec.type] || '💡'}</span>
                <span class="rec-priority" style="background: ${priorityColors[rec.priority]}">${rec.priority.toUpperCase()}</span>
            </div>
            <h3 class="rec-title">${rec.title}</h3>
            <p class="rec-message">${rec.message}</p>
            <div class="rec-action">
                <strong>Action:</strong> ${rec.action}
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Create advanced forecast chart with confidence intervals
function createAdvancedForecastChart(forecastData) {
    const ctx = document.getElementById('advancedForecastChart').getContext('2d');
    
    if (advancedForecastChart) {
        advancedForecastChart.destroy();
    }
    
    // Prepare historical data (last 60 days for cleaner view)
    const historicalSlice = historicalData.slice(-60);
    const historicalDates = historicalSlice.map(d => d.Date);
    const historicalValues = historicalSlice.map(d => d.Total_Quantity);
    
    // Prepare forecast data
    const forecastDates = forecastData.map(d => d.Date);
    const forecasts = forecastData.map(d => d.Forecast);
    const lowerBounds = forecastData.map(d => d.Lower_Bound);
    const upperBounds = forecastData.map(d => d.Upper_Bound);
    
    // Combine dates
    const allDates = [...historicalDates, ...forecastDates];
    
    advancedForecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [
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
                    label: 'AI Forecast',
                    data: [...Array(historicalDates.length).fill(null), ...forecasts],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: '95% Confidence Interval',
                    data: [...Array(historicalDates.length).fill(null), ...upperBounds],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: '+1',
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: false, // Hide from legend
                    data: [...Array(historicalDates.length).fill(null), ...lowerBounds],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                }
            ]
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
                        boxHeight: 8,
                        filter: function(item) {
                            return item.text !== false;
                        }
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
                            if (label && label !== false) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += formatNumber(Math.round(context.parsed.y)) + ' units';
                            }
                            return label;
                        }
                    }
                },
                filler: {
                    propagate: true
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

// Load inventory recommendations
async function loadInventoryRecommendations() {
    try {
        const response = await apiCall('/api/advanced-forecast/inventory?safety_days=7');
        
        document.getElementById('invAvgDemand').textContent = formatNumber(response.data.avg_daily_demand) + ' units/day';
        document.getElementById('invMaxDemand').textContent = formatNumber(response.data.max_daily_demand) + ' units/day';
        document.getElementById('invSafetyStock').textContent = formatNumber(response.data.safety_stock) + ' units';
        document.getElementById('invReorderPoint').textContent = formatNumber(response.data.reorder_point) + ' units';
        document.getElementById('invOrderQty').textContent = formatNumber(response.data.recommended_order_quantity) + ' units';
        document.getElementById('invLeadTime').textContent = response.data.lead_time_days + ' days';
    } catch (error) {
        console.error('Error loading inventory recommendations:', error);
    }
}

// Populate daily forecast table
function populateDailyForecastTable(dailyData) {
    const tbody = document.getElementById('dailyForecastBody');
    tbody.innerHTML = '';
    
    dailyData.forEach(row => {
        const tr = document.createElement('tr');
        const range = row.Upper_Bound - row.Lower_Bound;
        
        tr.innerHTML = `
            <td><strong>${new Date(row.Date).toLocaleDateString()}</strong></td>
            <td>${row.Day_Name}</td>
            <td>Week ${row.Week}</td>
            <td><span class="forecast-value">${formatNumber(Math.round(row.Forecast))}</span></td>
            <td>${formatNumber(Math.round(row.Lower_Bound))}</td>
            <td>${formatNumber(Math.round(row.Upper_Bound))}</td>
            <td>±${formatNumber(Math.round(range / 2))}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Export daily forecast
function exportDailyForecast() {
    if (!dailyForecastData || dailyForecastData.length === 0) {
        showNotification('No forecast data to export', 'error');
        return;
    }
    
    const exportData = dailyForecastData.map(row => ({
        'Date': new Date(row.Date).toLocaleDateString(),
        'Day': row.Day_Name,
        'Week': row.Week,
        'Forecast': Math.round(row.Forecast),
        'Lower Bound': Math.round(row.Lower_Bound),
        'Upper Bound': Math.round(row.Upper_Bound),
        'Confidence Range': Math.round(row.Upper_Bound - row.Lower_Bound)
    }));
    
    const timestamp = new Date().toISOString().split('T')[0];
    exportToCSV(exportData, `ai_forecast_${timestamp}.csv`);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadInitialData();
});
