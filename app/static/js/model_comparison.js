// Model Comparison Dashboard
let baselineChart = null;
let metricsChart = null;
let featureImportanceChart = null;
let rocCurvesChart = null;

document.addEventListener('DOMContentLoaded', function() {
    loadSummary();
    loadBaselineComparison();
    loadTunedComparison();
    loadConfusionMatrices();
    loadROCCurves();
    loadFeatureImportance();
});

function loadSummary() {
    fetch('/api/model-comparison/summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySummary(data.data);
            }
        })
        .catch(error => console.error('Error loading summary:', error));
}

function displaySummary(summary) {
    const html = `
        <div class="summary-item">
            <h3>Total Baseline Models</h3>
            <div class="value">${summary.total_baseline_models}</div>
        </div>
        <div class="summary-item alt">
            <h3>Best Baseline F1</h3>
            <div class="value">${summary.best_baseline_f1}%</div>
        </div>
        <div class="summary-item">
            <h3>Avg Baseline F1</h3>
            <div class="value">${summary.avg_baseline_f1}%</div>
        </div>
        <div class="summary-item alt">
            <h3>Total Features</h3>
            <div class="value">${summary.total_features}</div>
        </div>
        <div class="summary-item">
            <h3>Training Samples</h3>
            <div class="value">${summary.training_samples}</div>
        </div>
        <div class="summary-item alt">
            <h3>Test Samples</h3>
            <div class="value">${summary.test_samples}</div>
        </div>
    `;
    document.getElementById('summary-content').innerHTML = html;
}

function loadBaselineComparison() {
    fetch('/api/model-comparison/baseline')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayBaselineTable(data.data);
                displayMetricsChart(data.data, 'baseline');
            }
        })
        .catch(error => console.error('Error loading baseline:', error));
}

function displayBaselineTable(models) {
    let html = '';
    let bestF1 = 0;
    let bestModel = null;

    models.forEach(model => {
        if (model.f1_score > bestF1) {
            bestF1 = model.f1_score;
            bestModel = model.model;
        }
    });

    models.forEach(model => {
        const isBest = model.model === bestModel ? 'best' : '';
        html += `
            <tr class="${isBest}">
                <td><strong>${model.model}</strong></td>
                <td>${model.accuracy}%</td>
                <td>${model.precision}%</td>
                <td>${model.recall}%</td>
                <td>${model.f1_score}%</td>
                <td>${model.roc_auc}%</td>
                <td>${model.specificity}%</td>
                <td>${model.cv_mean}% ± ${model.cv_std}%</td>
            </tr>
        `;
    });

    document.getElementById('baseline-body').innerHTML = html;
}

function loadTunedComparison() {
    fetch('/api/model-comparison/tuned')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayTunedTable(data.data);
            }
        })
        .catch(error => console.error('Error loading tuned models:', error));
}

function displayTunedTable(models) {
    let html = '';
    let bestF1 = 0;
    let bestModel = null;

    models.forEach(model => {
        if (model.f1_score > bestF1) {
            bestF1 = model.f1_score;
            bestModel = model.model;
        }
    });

    models.forEach(model => {
        const isBest = model.model === bestModel ? 'best' : '';
        const params = JSON.stringify(model.best_params).replace(/"/g, '');
        html += `
            <tr class="${isBest}">
                <td><strong>${model.model}</strong></td>
                <td>${model.accuracy}%</td>
                <td>${model.precision}%</td>
                <td>${model.recall}%</td>
                <td>${model.f1_score}%</td>
                <td>${model.roc_auc}%</td>
                <td>${model.specificity}%</td>
                <td><small>${params}</small></td>
            </tr>
        `;
    });

    document.getElementById('tuned-body').innerHTML = html;
}

function displayMetricsChart(models, type) {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    
    const labels = models.map(m => m.model);
    const datasets = [
        {
            label: 'Accuracy',
            data: models.map(m => m.accuracy),
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderColor: 'rgba(102, 126, 234, 1)',
            borderWidth: 2
        },
        {
            label: 'Precision',
            data: models.map(m => m.precision),
            backgroundColor: 'rgba(240, 147, 251, 0.8)',
            borderColor: 'rgba(240, 147, 251, 1)',
            borderWidth: 2
        },
        {
            label: 'Recall',
            data: models.map(m => m.recall),
            backgroundColor: 'rgba(245, 87, 108, 0.8)',
            borderColor: 'rgba(245, 87, 108, 1)',
            borderWidth: 2
        },
        {
            label: 'F1 Score',
            data: models.map(m => m.f1_score),
            backgroundColor: 'rgba(76, 175, 80, 0.8)',
            borderColor: 'rgba(76, 175, 80, 1)',
            borderWidth: 2
        },
        {
            label: 'ROC-AUC',
            data: models.map(m => m.roc_auc),
            backgroundColor: 'rgba(255, 193, 7, 0.8)',
            borderColor: 'rgba(255, 193, 7, 1)',
            borderWidth: 2
        }
    ];

    if (metricsChart) {
        metricsChart.destroy();
    }

    metricsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Model Performance Metrics Comparison'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                }
            }
        }
    });
}

function loadFeatureImportance() {
    const model = document.getElementById('model-selector').value;
    const topN = document.getElementById('top-n').value;

    fetch(`/api/model-comparison/feature-importance?model=${model}&top_n=${topN}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayFeatureImportance(data.data);
            }
        })
        .catch(error => console.error('Error loading feature importance:', error));
}

function displayFeatureImportance(features) {
    const ctx = document.getElementById('featureImportanceChart').getContext('2d');
    
    const labels = features.map(f => f.feature);
    const data = features.map(f => f.importance);

    if (featureImportanceChart) {
        featureImportanceChart.destroy();
    }

    featureImportanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Importance (%)',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Importance (%)'
                    }
                }
            }
        }
    });
}

function loadConfusionMatrices() {
    fetch('/api/model-comparison/confusion-matrices')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayConfusionMatrices(data.data);
            }
        })
        .catch(error => console.error('Error loading confusion matrices:', error));
}

function displayConfusionMatrices(matrices) {
    let html = '';

    for (const [modelName, matrix] of Object.entries(matrices)) {
        const accuracy = ((matrix.true_positives + matrix.true_negatives) / matrix.total * 100).toFixed(2);
        const sensitivity = (matrix.true_positives / (matrix.true_positives + matrix.false_negatives) * 100).toFixed(2);
        const specificity = (matrix.true_negatives / (matrix.true_negatives + matrix.false_positives) * 100).toFixed(2);

        html += `
            <div class="confusion-matrix">
                <h4>${modelName.replace(/_/g, ' ')}</h4>
                <div class="matrix-grid">
                    <div class="matrix-cell tp">
                        <div style="font-size: 0.75rem; opacity: 0.9; margin-bottom: 0.25rem;">True Positive</div>
                        <div style="font-size: 1.5rem; font-weight: 700;">${matrix.true_positives}</div>
                    </div>
                    <div class="matrix-cell fp">
                        <div style="font-size: 0.75rem; opacity: 0.9; margin-bottom: 0.25rem;">False Positive</div>
                        <div style="font-size: 1.5rem; font-weight: 700;">${matrix.false_positives}</div>
                    </div>
                    <div class="matrix-cell fn">
                        <div style="font-size: 0.75rem; opacity: 0.9; margin-bottom: 0.25rem;">False Negative</div>
                        <div style="font-size: 1.5rem; font-weight: 700;">${matrix.false_negatives}</div>
                    </div>
                    <div class="matrix-cell tn">
                        <div style="font-size: 0.75rem; opacity: 0.9; margin-bottom: 0.25rem;">True Negative</div>
                        <div style="font-size: 1.5rem; font-weight: 700;">${matrix.true_negatives}</div>
                    </div>
                </div>
                <div class="metrics-summary">
                    <div>
                        <span>Accuracy:</span>
                        <strong>${accuracy}%</strong>
                    </div>
                    <div>
                        <span>Sensitivity:</span>
                        <strong>${sensitivity}%</strong>
                    </div>
                    <div>
                        <span>Specificity:</span>
                        <strong>${specificity}%</strong>
                    </div>
                </div>
            </div>
        `;
    }

    document.getElementById('confusion-matrices').innerHTML = html;
}

function loadROCCurves() {
    fetch('/api/model-comparison/roc-curves')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayROCCurves(data.data);
            }
        })
        .catch(error => console.error('Error loading ROC curves:', error));
}

function displayROCCurves(rocData) {
    const ctx = document.getElementById('rocCurvesChart').getContext('2d');
    
    const colors = [
        'rgba(102, 126, 234, 1)',
        'rgba(240, 147, 251, 1)',
        'rgba(245, 87, 108, 1)',
        'rgba(76, 175, 80, 1)'
    ];

    const datasets = [];
    let colorIndex = 0;

    for (const [modelName, rocCurve] of Object.entries(rocData)) {
        // Sort by FPR to ensure proper line drawing
        const sortedData = rocCurve.fpr.map((fpr, i) => ({
            x: fpr,
            y: rocCurve.tpr[i]
        })).sort((a, b) => a.x - b.x);
        
        datasets.push({
            label: `${modelName.replace(/_/g, ' ')} (AUC: ${rocCurve.auc.toFixed(3)})`,
            data: sortedData,
            borderColor: colors[colorIndex % colors.length],
            backgroundColor: 'transparent',
            borderWidth: 2,
            fill: false,
            tension: 0,
            pointRadius: 0,
            pointHoverRadius: 4
        });
        colorIndex++;
    }

    // Add diagonal line
    datasets.push({
        label: 'Random Classifier',
        data: [{x: 0, y: 0}, {x: 1, y: 1}],
        borderColor: 'rgba(200, 200, 200, 0.5)',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 0
    });

    if (rocCurvesChart) {
        rocCurvesChart.destroy();
    }

    rocCurvesChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'ROC Curves Comparison'
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'False Positive Rate'
                    },
                    min: 0,
                    max: 1
                },
                y: {
                    title: {
                        display: true,
                        text: 'True Positive Rate'
                    },
                    min: 0,
                    max: 1
                }
            }
        }
    });
}
