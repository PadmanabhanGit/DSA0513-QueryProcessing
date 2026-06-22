async function fetchStats() {
  const res = await fetch('/api/stats');
  return res.json();
}

function renderCards(stats) {
  document.getElementById('totalQueries').innerText = stats.total_queries || 0;
  document.getElementById('slowQueries').innerText = stats.slow_queries || 0;
  document.getElementById('avgTime').innerText = (stats.avg_time || 0).toFixed(2) + ' ms';
  document.getElementById('optimizations').innerText = stats.optimizations || 0;
}

function renderCharts(stats) {
  // Execution trend
  const ctx = document.getElementById('timeTrend').getContext('2d');
  if (window.timeTrendChart) window.timeTrendChart.destroy();
  window.timeTrendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: stats.trend.labels || [],
      datasets: [{ label: 'Execution Time (ms)', data: stats.trend.data || [], borderColor: 'rgba(75,192,192,1)', fill:false }]
    }
  });

  // Status distribution
  const ctx2 = document.getElementById('statusDist').getContext('2d');
  if (window.statusChart) window.statusChart.destroy();
  window.statusChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
      labels: Object.keys(stats.status || {}),
      datasets: [{ data: Object.values(stats.status || {}), backgroundColor:['#4e73df','#1cc88a','#e74a3b'] }]
    }
  });
}

async function initDashboard(){
  const stats = await fetchStats();
  renderCards(stats);
  renderCharts(stats);
}

document.addEventListener('DOMContentLoaded', ()=>{
  if (document.getElementById('timeTrend')) initDashboard();
  // dark mode toggle
  const toggle = document.getElementById('darkToggle');
  if(toggle){
    toggle.addEventListener('click', ()=>{
      document.body.classList.toggle('dark');
      localStorage.setItem('dark', document.body.classList.contains('dark'));
    });
    if(localStorage.getItem('dark')==='true') document.body.classList.add('dark');
  }
});
