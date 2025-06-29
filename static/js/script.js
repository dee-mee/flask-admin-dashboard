// script.js
document.addEventListener('DOMContentLoaded', function () {
    // Fetch and display dashboard stats
    fetch('/api/dashboard_stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-users').textContent = data.total_users;
            document.getElementById('total-revenue').textContent = '$' + data.total_revenue.toFixed(2);
            document.getElementById('new-orders').textContent = data.new_orders;
            document.getElementById('messages').textContent = data.messages;
        })
        .catch(error => console.error('Error fetching dashboard stats:', error));

    // Fetch and display sales data for the chart
    fetch('/api/sales_data')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.month);
            const salesData = data.map(item => item.amount);

            const salesChartCanvas = document.getElementById('salesChart').getContext('2d');
            new Chart(salesChartCanvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Sales',
                        data: salesData,
                        backgroundColor: 'rgba(0, 255, 0, 0.2)',
                        borderColor: 'rgba(0, 255, 0, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#00ff00' // Green color for legend text
                            }
                        }
                    }
                }
            });
        });

    // Fetch and display recent orders
    fetch('/api/orders')
        .then(response => response.json())
        .then(orders => {
            const ordersTableBody = document.getElementById('orders-table-body');
            ordersTableBody.innerHTML = ''; // Clear existing sample data
            orders.forEach(order => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${order.id}</td>
                    <td>${order.customer}</td>
                    <td>${order.product}</td>
                    <td>$${order.amount.toFixed(2)}</td>
                    <td><span class="badge bg-${order.status === 'Completed' ? 'success' : order.status === 'Pending' ? 'warning' : 'danger'}">${order.status}</span></td>
                `;
                ordersTableBody.appendChild(row);
            });
        });

    // Fetch and display recent activities
    fetch('/api/activities')
        .then(response => response.json())
        .then(activities => {
            const activityList = document.getElementById('activity-list');
            activityList.innerHTML = ''; // Clear existing sample data
            activities.forEach(activity => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = activity.description;
                activityList.appendChild(listItem);
            });
        });
});
