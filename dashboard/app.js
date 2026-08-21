document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const runBacktestBtn = document.getElementById('run-backtest-btn');
    const runScanBtn = document.getElementById('run-scan-btn');
    const runScanFastBtn = document.getElementById('run-scan-fast-btn');
    const signalsBody = document.getElementById('signals-body');
    const backtestLoader = document.getElementById('backtest-loader');
    const scanLoader = document.getElementById('scan-loader');
    
    // Stats Elements
    const equityVal = document.getElementById('equity-val');
    const winrateVal = document.getElementById('winrate-val');
    const riskVal = document.getElementById('risk-val');
    
    // Chart Instance
    let equityChart = null;
    let tvChart = null;
    let tvCandleSeries = null;
    
    // Sidebar Navigation Elements
    const navDashboard = document.getElementById('nav-dashboard');
    const navScanner = document.getElementById('nav-scanner');
    const navBacktest = document.getElementById('nav-backtest');

    // Initialize
    fetchPortfolioStats();
    initChart();
    
    // Event Listeners
    runBacktestBtn.addEventListener('click', runBacktest);
    runScanBtn.addEventListener('click', () => runScan(false));
    runScanFastBtn.addEventListener('click', () => runScan(true));

    // Navigation Listeners
    navDashboard.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        updateActiveNav(navDashboard);
    });

    navScanner.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('signals-container').scrollIntoView({ behavior: 'smooth' });
        updateActiveNav(navScanner);
    });

    navBacktest.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('chart-container').scrollIntoView({ behavior: 'smooth' });
        updateActiveNav(navBacktest);
    });

    function updateActiveNav(activeElement) {
        document.querySelectorAll('.sidebar nav li').forEach(li => li.classList.remove('active'));
        activeElement.parentElement.classList.add('active');
    }
    
    // Functions
    async function fetchPortfolioStats() {
        try {
            const res = await fetch('/api/portfolio');
            const data = await res.json();
            equityVal.textContent = `$${data.balance.toLocaleString()}`;
            riskVal.textContent = `${data.risk_per_trade_pct * 100}%`;
        } catch (error) {
            console.error("Error fetching portfolio:", error);
        }
    }
    
    function initChart() {
        const ctx = document.getElementById('equityChart').getContext('2d');
        
        // Gradient for chart area
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.5)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
        
        equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Account Equity ($)',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { 
                            color: '#94a3b8',
                            callback: (value) => '$' + value
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
    
    async function runBacktest() {
        backtestLoader.classList.remove('hidden');
        try {
            const res = await fetch('/api/backtest');
            const data = await res.json();
            
            if (data.status === 'success') {
                updateBacktestUI(data);
            } else {
                alert("Error running backtest: " + data.message);
            }
        } catch (error) {
            console.error(error);
            alert("Failed to run backtest");
        } finally {
            backtestLoader.classList.add('hidden');
        }
    }
    
    function updateBacktestUI(data) {
        const { summary, trades } = data;
        
        // Update Stats
        equityVal.textContent = `$${summary.final_equity.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        const winrate = summary.total_trades > 0 ? (summary.wins / summary.total_trades) * 100 : 0;
        winrateVal.textContent = `${winrate.toFixed(1)}%`;
        
        const trendEl = equityVal.nextElementSibling;
        if (summary.return_pct > 0) {
            trendEl.className = 'trend positive';
            trendEl.innerHTML = `<i class="fa-solid fa-arrow-up"></i> +${summary.return_pct.toFixed(2)}%`;
        } else {
            trendEl.className = 'trend negative';
            trendEl.innerHTML = `<i class="fa-solid fa-arrow-down"></i> ${summary.return_pct.toFixed(2)}%`;
        }
        
        const winrateTrend = winrateVal.nextElementSibling;
        winrateTrend.textContent = `${summary.total_trades} Trades`;
        
        // Update Chart
        let currentEquity = summary.initial_balance;
        const labels = ['Start'];
        const equityData = [currentEquity];
        
        trades.forEach(trade => {
            labels.push(trade.time);
            equityData.push(trade.equity);
        });
        
        equityChart.data.labels = labels;
        equityChart.data.datasets[0].data = equityData;
        equityChart.update();
    }
    
    async function runScan(fast) {
        scanLoader.classList.remove('hidden');
        try {
            const res = await fetch(`/api/scan?fast=${fast}`);
            const data = await res.json();
            
            if (data.status === 'success') {
                updateSignalsTable(data.data);
            } else {
                alert("Error running scan: " + data.message);
            }
        } catch (error) {
            console.error(error);
            alert("Failed to run scan");
        } finally {
            scanLoader.classList.add('hidden');
        }
    }
    
    function updateSignalsTable(signals) {
        signalsBody.innerHTML = '';
        
        if (signals.length === 0) {
            signalsBody.innerHTML = `<tr class="empty-state-row"><td colspan="6" class="empty-state">No actionable signals found at this time.</td></tr>`;
            return;
        }
        
        signals.forEach(sig => {
            const actionClass = sig.action === 'BUY' ? 'buy' : 'sell';
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.onclick = () => loadCandleChart(sig.ticker, sig.pair);
            row.innerHTML = `
                <td>
                    <strong>${sig.pair}</strong><br>
                    <small style="color:var(--text-muted)">${sig.ticker}</small>
                </td>
                <td><span class="badge ${actionClass}">${sig.action}</span></td>
                <td>${sig.entry.toFixed(5)}</td>
                <td>${sig.stop_loss.toFixed(5)}</td>
                <td>${sig.take_profit.toFixed(5)}</td>
                <td>$${sig.dollar_risk.toFixed(2)}<br><small style="color:var(--text-muted)">${sig.lot_size} Lots</small></td>
            `;
            signalsBody.appendChild(row);
        });
    }

    async function loadCandleChart(ticker, pairName) {
        const chartSection = document.getElementById('tv-chart-section');
        const chartTitle = document.getElementById('tv-chart-title');
        const chartContainer = document.getElementById('tv-chart-container');
        
        chartSection.style.display = 'block';
        chartTitle.textContent = `Live Chart: ${pairName} (${ticker})`;
        
        chartSection.scrollIntoView({ behavior: 'smooth' });
        
        try {
            const res = await fetch(`/api/candles?ticker=${ticker}`);
            const data = await res.json();
            
            if (data.status !== 'success') {
                alert('Failed to load chart data');
                return;
            }
            
            if (!tvChart) {
                tvChart = LightweightCharts.createChart(chartContainer, {
                    width: chartContainer.clientWidth,
                    height: 400,
                    layout: {
                        background: { type: 'solid', color: 'transparent' },
                        textColor: '#e2e8f0',
                    },
                    grid: {
                        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
                    },
                    crosshair: {
                        mode: LightweightCharts.CrosshairMode.Normal,
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                    },
                    timeScale: {
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                    },
                });
                tvCandleSeries = tvChart.addCandlestickSeries({
                    upColor: '#22c55e',
                    downColor: '#ef4444',
                    borderVisible: false,
                    wickUpColor: '#22c55e',
                    wickDownColor: '#ef4444',
                });
                
                new ResizeObserver(entries => {
                    if (entries.length === 0 || entries[0].target !== chartContainer) { return; }
                    const newRect = entries[0].contentRect;
                    tvChart.applyOptions({ height: newRect.height, width: newRect.width });
                }).observe(chartContainer);
            }
            
            tvCandleSeries.setData(data.data);
            tvChart.timeScale().fitContent();
            
        } catch(err) {
            console.error(err);
        }
    }
});
