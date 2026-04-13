const CHART_COLORS = {
    primary: '#4f46e5',
    secondary: '#7c3aed',
    success: '#059669',
    warning: '#d97706',
    danger: '#dc2626',
};

const defaultChartOptions = {
    responsive: true,
    animation: { duration: 800 },
    plugins: {
        legend: { position: 'bottom' },
    },
};

function buildBarOptions(yLabel) {
    return {
        ...defaultChartOptions,
        scales: {
            y: {
                beginAtZero: true,
                title: { display: !!yLabel, text: yLabel },
                grid: { color: '#f1f5f9' },
            },
            x: { grid: { display: false } },
        },
    };
}
