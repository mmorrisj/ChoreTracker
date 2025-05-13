import './App.css';
import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function App() {
  const myChartRef = useRef(null);
  const timelineChartRef = useRef(null);
  const earningsExpensesChartRef = useRef(null);

  const children = [
    { id: 1, name: 'Virginia' },
    { id: 2, name: 'Evelyn' },
    { id: 3, name: 'Lucy' }
  ];

  useEffect(() => {
    const ctx1 = myChartRef.current.getContext('2d');
    const ctx2 = timelineChartRef.current.getContext('2d');
    const ctx3 = earningsExpensesChartRef.current.getContext('2d');

    // Destroy previous charts if they exist
    Chart.getChart(ctx1)?.destroy();
    Chart.getChart(ctx2)?.destroy();
    Chart.getChart(ctx3)?.destroy();

    new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: children.map(c => c.name),
        datasets: [{
          label: 'Net Earnings',
          data: [20, 35, 15], // Replace with dynamic values
          backgroundColor: ['#4caf50', '#2196f3', '#ff9800']
        }]
      }
    });

    new Chart(ctx2, {
      type: 'line',
      data: {
        labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
        datasets: children.map((c, idx) => ({
          label: c.name,
          data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 3)),
          borderColor: ['#4caf50', '#2196f3', '#ff9800'][idx],
          fill: false
        }))
      }
    });

    new Chart(ctx3, {
      type: 'doughnut',
      data: {
        labels: ['Earnings', 'Expenses', 'Deductions'],
        datasets: [{
          data: [50, 20, 10], // Example data
          backgroundColor: ['#4caf50', '#f44336', '#ff9800']
        }]
      }
    });
  }, []);

  return (
    <div className="container">
      <h1>Select a Child</h1>
      {children.map(child => (
        <button
          key={child.id}
          className="child-button"
          onClick={() => window.location.href = `/manage-chores/${child.id}`}
        >
          {child.name}
        </button>
      ))}

      <h2>Children's Net Earnings</h2>
      <div className="chart-container">
        <canvas ref={myChartRef} width="400" height="100"></canvas>
      </div>

      <h2>Chore Completion in Last 30 Days</h2>
      <div className="chart-container">
        <canvas ref={timelineChartRef} width="400" height="200"></canvas>
      </div>

      <a href="/settings" className="button-link">Settings</a>

      <h2>Earnings, Expenses, and Deductions Breakdown</h2>
      <div className="chart-container">
        <canvas ref={earningsExpensesChartRef} width="400" height="200"></canvas>
      </div>
    </div>
  );
}

export default App;
