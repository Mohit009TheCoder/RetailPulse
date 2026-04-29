// Customers page JavaScript

let currentCustomers = [];

// Load customers data
async function loadCustomers(segment = '', customerId = '') {
    try {
        let url = '/api/customers?limit=1000';
        if (segment) url += `&segment=${encodeURIComponent(segment)}`;
        if (customerId) url += `&customer_id=${encodeURIComponent(customerId)}`;
        
        const data = await apiCall(url);
        currentCustomers = data.data;
        populateCustomersTable(data.data);
        updateCustomerCount(data.count);
        
        if (data.count > 0) {
            showNotification(`Loaded ${data.count} customers`, 'success');
        } else {
            showNotification('No customers found', 'info');
        }
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

// Populate customers table
function populateCustomersTable(customers) {
    const tbody = document.getElementById('customersTableBody');
    tbody.innerHTML = '';
    
    if (customers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No customers found</td></tr>';
        return;
    }
    
    customers.forEach(customer => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${customer['Customer ID']}</strong></td>
            <td>
                <span style="display: inline-block; padding: 0.25rem 0.75rem; background: ${getSegmentColor(customer.Segment)}; color: white; border-radius: 1rem; font-size: 0.75rem; font-weight: 600;">
                    ${customer.Segment}
                </span>
            </td>
            <td>${customer.Recency} days</td>
            <td>${customer.Frequency}</td>
            <td>${formatCurrency(customer.Monetary)}</td>
            <td><span class="score-badge">${customer.R_Score}</span></td>
            <td><span class="score-badge">${customer.F_Score}</span></td>
            <td><span class="score-badge">${customer.M_Score}</span></td>
            <td><span class="score-badge total">${customer.RFM_Score}</span></td>
        `;
        tbody.appendChild(tr);
    });
    
    // Add score badge styles
    if (!document.getElementById('score-badge-styles')) {
        const style = document.createElement('style');
        style.id = 'score-badge-styles';
        style.textContent = `
            .score-badge {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                background: #e5e7eb;
                color: #374151;
                border-radius: 0.375rem;
                font-size: 0.875rem;
                font-weight: 600;
            }
            .score-badge.total {
                background: #6366f1;
                color: white;
            }
        `;
        document.head.appendChild(style);
    }
}

// Update customer count
function updateCustomerCount(count) {
    document.getElementById('customerCount').textContent = formatNumber(count);
}

// Filter customers by segment
function filterCustomers() {
    const segment = document.getElementById('segmentFilter').value;
    loadCustomers(segment);
}

// Search customer by ID
function searchCustomer() {
    const customerId = document.getElementById('customerSearch').value.trim();
    if (customerId) {
        loadCustomers('', customerId);
    } else {
        showNotification('Please enter a customer ID', 'error');
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('segmentFilter').value = '';
    document.getElementById('customerSearch').value = '';
    loadCustomers();
}

// Export customers data
function exportData() {
    if (currentCustomers.length === 0) {
        showNotification('No data to export', 'error');
        return;
    }
    
    const exportData = currentCustomers.map(customer => ({
        'Customer ID': customer['Customer ID'],
        'Segment': customer.Segment,
        'Recency (days)': customer.Recency,
        'Frequency': customer.Frequency,
        'Monetary': customer.Monetary.toFixed(2),
        'R Score': customer.R_Score,
        'F Score': customer.F_Score,
        'M Score': customer.M_Score,
        'RFM Score': customer.RFM_Score
    }));
    
    const timestamp = new Date().toISOString().split('T')[0];
    exportToCSV(exportData, `rfm_customers_${timestamp}.csv`);
}

// Initialize customers page
document.addEventListener('DOMContentLoaded', () => {
    // Check for segment parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const segment = urlParams.get('segment');
    
    if (segment) {
        document.getElementById('segmentFilter').value = segment;
        loadCustomers(segment);
    } else {
        loadCustomers();
    }
});
