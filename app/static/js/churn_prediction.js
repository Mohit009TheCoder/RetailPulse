// Churn Prediction JavaScript

let churnData = null;
let riskDistributionChart = null;
let churnProbabilityChart = null;
let riskMatrixChart = null;

// Load churn prediction data
async function loadChurnData() {
    try {
        showNotification('Analyzing customer churn risk...', 'info');
        
        // Load summary
        const summary = await apiCall('/api/churn/summary');
        console.log('Summary loaded:', summary);
        updateSummaryStats(summary.data);
        
        // Load recommendations
        const recommendations = await apiCall('/api/churn/recommendations');
        console.log('Recommendations loaded:', recommendations);
        displayRecommendations(recommendations.data);
        
        // Load risk distribution
        const distribution = await apiCall('/api/churn/risk-distribution');
        console.log('Distribution loaded:', distribution);
        createRiskDistributionChart(distribution.data);
        
        // Load predictions for probability chart
        const predictionsUrl = '/api/churn/predictions' + '?limit=1000';
        const predictions = await apiCall(predictionsUrl);
        console.log('Predictions loaded:', predictions.data.length, 'customers');
        churnData = predictions.data;
        createChurnProbabilityChart(predictions.data);
        createRiskMatrixChart(distribution.data);
        
        // Load model performance
        const performance = await apiCall('/api/churn/model-performance');
        console.log('Model performance loaded:', performance);
        populateModelPerformance(performance.data);
        
        // Load feature importance
        const features = await apiCall('/api/churn/feature-importance');
        console.log('Feature importance loaded:', features);
        populateFeatureImportance(features.data);
        
        // Load high risk customers
        const highRiskUrl = '/api/churn/high-risk' + '?limit=50';
        const highRisk = await apiCall(highRiskUrl);
        console.log('High risk customers loaded:', highRisk.data.length);
        populateHighRiskTable(highRisk.data);
        
        showNotification('Churn analysis complete!', 'success');
    } catch (error) {
        console.error('Error loading churn data:', error);
        showNotification('Error loading churn data: ' + error.message, 'error');
    }
}

// Update summary statistics
function updateSummaryStats(summary) {
    document.getElementById('totalCustomers').textContent = formatNumber(summary.total_customers);
    document.getElementById('churnRate').textContent = summary.churn_rate.toFixed(1) + '%';
    document.getElementById('highRiskCount').textContent = formatNumber(summary.high_risk_customers);
    document.getElementById('vipAtRisk').textContent = formatNumber(summary.high_value_at_risk);
}

// Display recommendations
function displayRecommendations(recommendations) {
    const grid = document.getElementById('recommendationsGrid');
    grid.innerHTML = '';
    
    const priorityColors = {
        'critical': '#ef4444',
        'high': '#f59e0b',
        'medium': '#3b82f6',
        'low': '#10b981'
    };
    
    recommendations.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.style.borderLeftColor = priorityColors[rec.priority];
        
        card.innerHTML = `
            <div class="rec-header">
                <span class="rec-icon">${rec.icon}</span>
                <span class="rec-priority" style="background: ${priorityColors[rec.priority]}">${rec.priority.toUpperCase()}</span>
            </div>
            <h3 class="rec-title">${rec.title}</h3>
            <p class="rec-message">${rec.message}</p>
            <div class="rec-action">
                <strong>Action:</strong> ${rec.action}
            </div>
            <div class="rec-count">
                <strong>Affected Customers:</strong> ${formatNumber(rec.count)}
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Create risk distribution chart
function createRiskDistributionChart(distribution) {
    const ctx = document.getElementById('riskDistributionChart').getContext('2d');
    
    if (riskDistributionChart) {
        riskDistributionChart.destroy();
    }
    
    // Aggregate by risk level
    const riskCounts = {};
    distribution.forEach(item => {
        if (!riskCounts[item.Risk_Level]) {
            riskCounts[item.Risk_Level] = 0;
        }
        riskCounts[item.Risk_Level] += item.Count;
    });
    
    const labels = Object.keys(riskCounts);
    const data = Object.values(riskCounts);
    
    const colors = {
        'Low Risk': '#10b981',
        'Medium Risk': '#f59e0b',
        'High Risk': '#ef4444'
    };
    
    const backgroundColors = labels.map(label => colors[label] || '#6b7280');
    
    riskDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 2,
                borderColor: '#ffffff'
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
                            size: 13,
                            family: 'Inter',
                            weight: '500'
                        },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
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
}

// Create churn probability distribution chart
function createChurnProbabilityChart(predictions) {
    const ctx = document.getElementById('churnProbabilityChart').getContext('2d');
    
    if (churnProbabilityChart) {
        churnProbabilityChart.destroy();
    }
    
    // Create histogram bins
    const bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
    const binCounts = new Array(bins.length - 1).fill(0);
    
    predictions.forEach(pred => {
        const prob = pred.Churn_Probability;
        for (let i = 0; i < bins.length - 1; i++) {
            if (prob >= bins[i] && prob < bins[i + 1]) {
                binCounts[i]++;
                break;
            }
        }
    });
    
    const labels = bins.slice(0, -1).map((bin, i) => `${(bin * 100).toFixed(0)}-${(bins[i + 1] * 100).toFixed(0)}%`);
    
    churnProbabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Customers',
                data: binCounts,
                backgroundColor: '#3b82f6',
                borderColor: '#2563eb',
                borderWidth: 1
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
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return 'Customers: ' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Customers',
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
                        text: 'Churn Probability Range',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Create risk matrix chart
function createRiskMatrixChart(distribution) {
    const ctx = document.getElementById('riskMatrixChart').getContext('2d');
    
    if (riskMatrixChart) {
        riskMatrixChart.destroy();
    }
    
    // Organize data by value segment and risk level
    const valueSegments = ['Low Value', 'Medium Value', 'High Value', 'VIP'];
    const riskLevels = ['Low Risk', 'Medium Risk', 'High Risk'];
    
    const datasets = riskLevels.map(risk => {
        const data = valueSegments.map(segment => {
            const item = distribution.find(d => d.Value_Segment === segment && d.Risk_Level === risk);
            return item ? item.Count : 0;
        });
        
        const colors = {
            'Low Risk': '#10b981',
            'Medium Risk': '#f59e0b',
            'High Risk': '#ef4444'
        };
        
        return {
            label: risk,
            data: data,
            backgroundColor: colors[risk],
            borderColor: '#ffffff',
            borderWidth: 2
        };
    });
    
    riskMatrixChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: valueSegments,
            datasets: datasets
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
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatNumber(context.parsed.y) + ' customers';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Customers',
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
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Customer Value Segment',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Populate model performance table
function populateModelPerformance(performance) {
    const tbody = document.getElementById('modelPerformanceBody');
    if (!tbody) {
        console.error('Model performance table body not found');
        return;
    }
    tbody.innerHTML = '';
    
    if (!performance || performance.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" class="text-center">No model data available</td></tr>';
        return;
    }
    
    performance.forEach(model => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${model.model}</strong></td>
            <td>${model.accuracy.toFixed(2)}%</td>
        `;
        tbody.appendChild(tr);
    });
}

// Populate feature importance table
function populateFeatureImportance(features) {
    const tbody = document.getElementById('featureImportanceBody');
    if (!tbody) {
        console.error('Feature importance table body not found');
        return;
    }
    tbody.innerHTML = '';
    
    if (!features || features.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" class="text-center">No feature data available</td></tr>';
        return;
    }
    
    features.forEach(feature => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${feature.Feature.replace(/_/g, ' ')}</strong></td>
            <td>
                <div class="importance-bar-container">
                    <div class="importance-bar" style="width: ${feature.Importance}%"></div>
                    <span class="importance-value">${feature.Importance.toFixed(2)}%</span>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Populate high risk customers table
function populateHighRiskTable(customers) {
    const tbody = document.getElementById('highRiskBody');
    if (!tbody) {
        console.error('High risk table body not found');
        return;
    }
    tbody.innerHTML = '';
    
    if (!customers || customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No high-risk customers found</td></tr>';
        return;
    }
    
    customers.forEach(customer => {
        const tr = document.createElement('tr');
        const riskClass = customer.Risk_Level.toLowerCase().replace(' ', '-');
        
        // Format recency display
        const recencyDisplay = customer.Recency_Category || `${customer.Recency_Days} days ago`;
        
        tr.innerHTML = `
            <td><strong>${customer.Customer_ID}</strong></td>
            <td><span class="badge badge-${riskClass}">${customer.Risk_Level}</span></td>
            <td>${(customer.Churn_Probability * 100).toFixed(1)}%</td>
            <td>${customer.Value_Segment}</td>
            <td>${formatCurrency(customer.Total_Spent)}</td>
            <td>${recencyDisplay}</td>
            <td>${customer.Unique_Invoices}</td>
            <td>${customer.RFM_Score}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Export high risk customers
function exportHighRisk() {
    if (!churnData || churnData.length === 0) {
        showNotification('No data to export', 'error');
        return;
    }
    
    const highRisk = churnData.filter(c => c.Risk_Level === 'High Risk' || c.Risk_Level === 'Medium Risk');
    
    const exportData = highRisk.map(customer => ({
        'Customer ID': customer.Customer_ID,
        'Risk Level': customer.Risk_Level,
        'Churn Probability': (customer.Churn_Probability * 100).toFixed(2) + '%',
        'Value Segment': customer.Value_Segment,
        'Total Spent': customer.Total_Spent.toFixed(2),
        'Last Purchase': customer.Recency_Category || (customer.Recency_Days + ' days ago'),
        'Recency Days': customer.Recency_Days,
        'Purchase Count': customer.Unique_Invoices,
        'RFM Score': customer.RFM_Score,
        'Purchase Frequency': customer.Purchase_Frequency ? customer.Purchase_Frequency.toFixed(3) : 'N/A'
    }));
    
    const timestamp = new Date().toISOString().split('T')[0];
    exportToCSV(exportData, `at_risk_customers_${timestamp}.csv`);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadChurnData();
});
