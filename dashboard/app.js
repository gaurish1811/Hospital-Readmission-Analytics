// Hospital Readmission Analytics - Chart.js & Interactive Filter Engine

document.addEventListener('DOMContentLoaded', () => {
    // Empirical metrics dataset derived from cleaning & SQL queries
    const baselineData = {
        age: {
            labels: ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100'],
            rates: [1.88, 5.80, 14.31, 11.26, 10.66, 9.77, 11.30, 12.06, 12.57, 11.90]
        },
        inpatient: {
            labels: ['0 Visits', '1 Visit', '2 Visits', '3+ Visits'],
            rates: [8.59, 13.25, 17.93, 26.40]
        },
        a1c: {
            labels: ['Not Tested', 'Normal (<7%)', '>7%', '>8%'],
            rates: [11.68, 9.77, 10.15, 9.94]
        },
        discharge: {
            labels: ['Home', 'SNF / ICF', 'Rehab / Transfer', 'Home Health', 'Left AMA', 'Outpatient/Other'],
            rates: [9.30, 14.36, 21.88, 12.71, 14.45, 12.30]
        }
    };

    // Global Chart Instances
    let chartAge, chartInpatient, chartA1c, chartDischarge;

    // Common Chart Options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleColor: '#f8fafc',
                bodyColor: '#38bdf8',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                callbacks: {
                    label: (context) => ` Readmission Rate: ${context.parsed.y || context.parsed.x}%`
                }
            }
        },
        scales: {
            x: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
            },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 }, callback: (v) => v + '%' }
            }
        }
    };

    // 1. Initialize Age Group Bar Chart
    function initAgeChart() {
        const ctx = document.getElementById('chart-age').getContext('2d');
        chartAge = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: baselineData.age.labels,
                datasets: [{
                    label: '30-Day Readmission Rate (%)',
                    data: baselineData.age.rates,
                    backgroundColor: baselineData.age.rates.map(r => r > 12 ? '#f43f5e' : (r > 10 ? '#38bdf8' : '#6366f1')),
                    borderRadius: 6
                }]
            },
            options: commonOptions
        });
    }

    // 2. Initialize Prior Inpatient Visits Chart
    function initInpatientChart() {
        const ctx = document.getElementById('chart-inpatient').getContext('2d');
        chartInpatient = new Chart(ctx, {
            type: 'line',
            data: {
                labels: baselineData.inpatient.labels,
                datasets: [{
                    label: 'Readmission Rate (%)',
                    data: baselineData.inpatient.rates,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.15)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#fbbf24'
                }]
            },
            options: commonOptions
        });
    }

    // 3. Initialize HbA1c Test Result Chart
    function initA1cChart() {
        const ctx = document.getElementById('chart-a1c').getContext('2d');
        chartA1c = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: baselineData.a1c.labels,
                datasets: [{
                    label: 'Readmission Rate (%)',
                    data: baselineData.a1c.rates,
                    backgroundColor: ['#64748b', '#10b981', '#38bdf8', '#a855f7'],
                    borderRadius: 6
                }]
            },
            options: commonOptions
        });
    }

    // 4. Initialize Discharge Disposition Chart
    function initDischargeChart() {
        const ctx = document.getElementById('chart-discharge').getContext('2d');
        chartDischarge = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: baselineData.discharge.labels,
                datasets: [{
                    label: 'Readmission Rate (%)',
                    data: baselineData.discharge.rates,
                    backgroundColor: baselineData.discharge.rates.map(r => r > 15 ? '#f43f5e' : '#38bdf8'),
                    borderRadius: 6
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y', // Horizontal Bar Chart
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', callback: (v) => v + '%' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#f8fafc', font: { family: 'Inter', size: 11 } }
                    }
                }
            }
        });
    }

    // Filter Logic & Interactive Metric Updates
    function applyFilters() {
        const ageVal = document.getElementById('filter-age').value;
        const a1cVal = document.getElementById('filter-a1c').value;
        const inpatVal = document.getElementById('filter-inpatient').value;

        let rateMultiplier = 1.0;
        let totalCount = 99343;

        if (ageVal !== 'ALL') rateMultiplier *= 1.05;
        if (a1cVal === '>8') rateMultiplier *= 0.92;
        if (inpatVal === '3+') rateMultiplier *= 2.31;
        else if (inpatVal === '2') rateMultiplier *= 1.57;

        const updatedRate = (11.39 * rateMultiplier).toFixed(2);
        document.getElementById('kpi-rate').innerText = `${updatedRate}%`;
        document.getElementById('kpi-count').innerText = `${Math.round(totalCount * (updatedRate / 100)).toLocaleString()} Encounters`;

        // Subtle animation pulse
        const kpiRateElem = document.getElementById('kpi-rate');
        kpiRateElem.style.color = updatedRate > 15 ? '#f43f5e' : '#ffffff';
    }

    // Attach Event Listeners
    document.getElementById('filter-age').addEventListener('change', applyFilters);
    document.getElementById('filter-a1c').addEventListener('change', applyFilters);
    document.getElementById('filter-inpatient').addEventListener('change', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', () => {
        document.getElementById('filter-age').value = 'ALL';
        document.getElementById('filter-a1c').value = 'ALL';
        document.getElementById('filter-inpatient').value = 'ALL';
        document.getElementById('kpi-rate').innerText = '11.39%';
        document.getElementById('kpi-rate').style.color = '#ffffff';
        document.getElementById('kpi-count').innerText = '11,314 out of 99,343 Encounters';
    });

    // Render All Charts
    initAgeChart();
    initInpatientChart();
    initA1cChart();
    initDischargeChart();
});
