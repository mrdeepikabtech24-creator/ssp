document.addEventListener('DOMContentLoaded', () => {
    loadSummary();
    loadWeeklyProgress();
    loadSubjectBreakdown();
    loadStreak();
});

function animateCount(el, target) {
    const duration = 800;
    const start = performance.now();
    const from = 0;
    function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.round(from + (target - from) * progress);
        el.textContent = typeof target === 'string' && target.includes('%')
            ? value + '%'
            : value;
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

function loadSummary() {
    fetch('/analytics/api/summary')
        .then(r => r.json())
        .then(data => {
            animateCount(document.getElementById('stat-total'), data.total);
            animateCount(document.getElementById('stat-completed'), data.completed);
            animateCount(document.getElementById('stat-pending'), data.pending);
            const rateEl = document.getElementById('stat-rate');
            if (rateEl) {
                const duration = 800;
                const start = performance.now();
                function step(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    rateEl.textContent = Math.round(data.completion_rate * progress) + '%';
                    if (progress < 1) requestAnimationFrame(step);
                }
                requestAnimationFrame(step);
            }
        })
        .catch(() => {});
}

function loadWeeklyProgress() {
    fetch('/analytics/api/weekly_progress')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('weekly-chart');
            if (!ctx) return;
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(d => {
                        const date = new Date(d.date);
                        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
                    }),
                    datasets: [{
                        label: 'Tasks Completed',
                        data: data.map(d => d.completed),
                        backgroundColor: 'rgba(79, 70, 229, 0.7)',
                        borderColor: '#4f46e5',
                        borderWidth: 2,
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    animation: { duration: 800 },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: ctx => ` ${ctx.parsed.y} task${ctx.parsed.y !== 1 ? 's' : ''} completed`
                            }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f1f5f9' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        })
        .catch(() => {});
}

function loadSubjectBreakdown() {
    fetch('/analytics/api/subject_breakdown')
        .then(r => r.json())
        .then(data => {
            const statusCtx = document.getElementById('status-chart');
            if (statusCtx) {
                fetch('/analytics/api/summary').then(r => r.json()).then(summary => {
                    new Chart(statusCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Completed', 'In Progress', 'Pending'],
                            datasets: [{
                                data: [summary.completed, summary.in_progress, summary.pending],
                                backgroundColor: ['#059669', '#4f46e5', '#d97706'],
                                borderWidth: 2,
                                borderColor: '#fff',
                            }]
                        },
                        options: {
                            responsive: true,
                            animation: { duration: 800 },
                            plugins: {
                                legend: { position: 'bottom' },
                                tooltip: {
                                    callbacks: {
                                        label: ctx => ` ${ctx.label}: ${ctx.parsed}`
                                    }
                                }
                            }
                        }
                    });
                });
            }

            const subjectCtx = document.getElementById('subject-chart');
            if (!subjectCtx || !data.length) return;
            new Chart(subjectCtx, {
                type: 'bar',
                data: {
                    labels: data.map(d => d.subject),
                    datasets: [{
                        label: 'Estimated Hours',
                        data: data.map(d => d.hours),
                        backgroundColor: data.map((_, i) => `hsl(${(i * 47 + 240) % 360}, 65%, 55%)`),
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    animation: { duration: 800 },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: ctx => ` ${ctx.parsed.y} hrs`
                            }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        })
        .catch(() => {});
}

function loadStreak() {
    fetch('/analytics/api/streak')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('streak-count');
            if (el) animateCount(el, data.streak);
        })
        .catch(() => {});
}
