const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const DAY_START_HOUR = 7;
const SLOT_HEIGHT_PX = 40;

function subjectColor(subject) {
    if (!subject || subject === 'Break') return '#94a3b8';
    let hash = 0;
    for (let i = 0; i < subject.length; i++) {
        hash = subject.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 60%, 45%)`;
}

function timeToMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + m;
}

function renderSlots(slots) {
    document.querySelectorAll('.timetable-slot').forEach(el => el.remove());

    const legend = document.getElementById('slot-legend');
    const subjects = new Set();

    slots.forEach(slot => {
        const dayIndex = DAYS.indexOf(slot.day_of_week);
        if (dayIndex === -1) return;

        const startMins = timeToMinutes(slot.start_time);
        const endMins = timeToMinutes(slot.end_time);
        const durationMins = endMins - startMins;

        const startOffsetMins = startMins - DAY_START_HOUR * 60;
        const topPx = (startOffsetMins / 60) * SLOT_HEIGHT_PX;
        const heightPx = (durationMins / 60) * SLOT_HEIGHT_PX;

        const startHour = Math.floor(startMins / 60);
        const cell = document.querySelector(
            `.time-cell[data-day="${slot.day_of_week}"][data-hour="${startHour}"]`
        );
        if (!cell) return;

        const div = document.createElement('div');
        div.className = 'timetable-slot' + (slot.slot_type === 'break' ? ' break-slot' : '');
        div.style.backgroundColor = subjectColor(slot.subject);
        div.style.top = `${(startMins % 60) / 60 * SLOT_HEIGHT_PX}px`;
        div.style.height = `${heightPx}px`;
        div.title = `${slot.subject} | ${slot.start_time} - ${slot.end_time}`;
        div.textContent = slot.subject;
        cell.appendChild(div);

        if (slot.slot_type !== 'break') subjects.add(slot.subject);
    });

    if (legend) {
        legend.innerHTML = '<div class="d-flex flex-wrap gap-2">' +
            [...subjects].map(s =>
                `<span class="badge" style="background:${subjectColor(s)}">${s}</span>`
            ).join('') +
        '</div>';
    }
}

function loadSlots() {
    fetch('/timetable/api/slots')
        .then(r => r.json())
        .then(renderSlots)
        .catch(() => {});
}

document.addEventListener('DOMContentLoaded', loadSlots);
