document.addEventListener('DOMContentLoaded', function() {
    const categories = earningsData.map(item => item.name);
    const values = earningsData.map(item => item.net_earnings);
    
    const earningsCtx = document.getElementById('myChart').getContext('2d');
    
    new Chart(earningsCtx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Net Earnings ($)',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100
                }
            },
            barThickness: 25,
            plugins: {
                legend: { display: false },
                datalabels: {
                    anchor: 'end',
                    align: 'right',
                    formatter: (value) => '$' + value.toFixed(2),
                    color: '#000',
                    font: { weight: 'bold' }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
});

document.addEventListener('DOMContentLoaded', async function() {
    const childrenNames = Object.keys(choreTimelineData);
    const datasets = childrenNames.map(child => ({
        label: child,
        data: choreTimelineData[child].map(entry => entry.count),
        backgroundColor: getRandomColor()
    }));

    const labels = choreTimelineData[childrenNames[0]].map(entry => entry.date);

    const timelineChartCtx = document.getElementById('completedChoresTimelineChart').getContext('2d');
    new Chart(timelineChartCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'Chores Completed' }, beginAtZero: true }
            },
            plugins: {
                legend: { display: true },
                title: { display: true, text: 'Chore Timeline' }
            }
        }
    });
});    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const children = earningsExpensesData.map(item => item.name);
    const earnings = earningsExpensesData.map(item => item.earnings);
    const expenses = earningsExpensesData.map(item => Math.abs(item.expenses));
    const deductions = earningsExpensesData.map(item => item.deductions);

    const chartCtx = document.getElementById('earningsExpensesChart').getContext('2d');

    new Chart(chartCtx, {
        type: 'bar',
        data: {
            labels: children,
            datasets: [
                {
                    label: 'Earnings',
                    data: earnings,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Expenses',
                    data: expenses,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Deductions',
                    data: deductions,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',  // Makes the bar chart horizontal
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    title: { display: true, text: 'Amount ($)' }
                },
                y: {
                    title: { display: true, text: 'Children' },
                    ticks: {
                        autoSkip: false,
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                legend: { display: true }
            },
            layout: {
                padding: {
                    left: 10,
                    right: 10,
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
});