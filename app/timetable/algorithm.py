from datetime import datetime, timedelta, time, date
from ..models import TimetableSlot

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAY_START = time(7, 0)
DAY_END = time(22, 0)
BREAK_AFTER_MINUTES = 90
BREAK_DURATION = 15


class TimetableGenerator:
    def __init__(self, user_id, study_hours_per_day=8, break_duration=BREAK_DURATION):
        self.user_id = user_id
        self.study_hours_per_day = study_hours_per_day
        self.break_duration = break_duration
        self.total_available_minutes = study_hours_per_day * 60 * 7

    def generate(self, tasks):
        if not tasks:
            return []
        weighted = [(t, self._weight(t)) for t in tasks]
        allocations = self._allocate_hours(weighted)
        return self._create_slots(allocations)

    def _calculate_urgency(self, deadline):
        if deadline is None:
            return 0.0
        now = datetime.utcnow()
        days_left = (deadline - now).total_seconds() / 86400
        return max(0.0, 10.0 - days_left)

    def _weight(self, task):
        urgency = self._calculate_urgency(task.deadline)
        return (task.difficulty * 2) + urgency

    def _allocate_hours(self, weighted_tasks):
        total_weight = sum(w for _, w in weighted_tasks)
        if total_weight == 0:
            total_weight = 1
        allocations = {}
        for task, weight in weighted_tasks:
            proportion = weight / total_weight
            minutes = proportion * self.total_available_minutes
            if task.estimated_hours:
                minutes = min(minutes, task.estimated_hours * 60)
            allocations[task.id] = {'task': task, 'minutes': max(30, minutes)}
        return allocations

    def _create_slots(self, allocations):
        slots = []
        week_number = datetime.utcnow().isocalendar()[1]

        task_list = sorted(
            allocations.values(),
            key=lambda x: self._calculate_urgency(x['task'].deadline),
            reverse=True
        )

        day_index = 0
        for item in task_list:
            task = item['task']
            remaining_minutes = item['minutes']

            while remaining_minutes > 0 and day_index < 7:
                day = DAYS[day_index]
                slot_minutes = min(remaining_minutes, BREAK_AFTER_MINUTES)

                current_start = self._next_available_time(slots, day)
                if current_start is None:
                    day_index += 1
                    continue

                slot_end_dt = datetime.combine(date.today(), current_start) + timedelta(minutes=slot_minutes)
                slot_end = slot_end_dt.time()

                if slot_end > DAY_END:
                    day_index += 1
                    continue

                slot = TimetableSlot(
                    user_id=self.user_id,
                    task_id=task.id,
                    day_of_week=day,
                    start_time=current_start,
                    end_time=slot_end,
                    subject=task.subject or task.title,
                    slot_type='study',
                    week_number=week_number,
                )
                slots.append(slot)
                remaining_minutes -= slot_minutes

                break_start_dt = slot_end_dt
                break_end_dt = break_start_dt + timedelta(minutes=self.break_duration)
                if break_end_dt.time() <= DAY_END:
                    break_slot = TimetableSlot(
                        user_id=self.user_id,
                        task_id=None,
                        day_of_week=day,
                        start_time=break_start_dt.time(),
                        end_time=break_end_dt.time(),
                        subject='Break',
                        slot_type='break',
                        week_number=week_number,
                    )
                    slots.append(break_slot)

                if remaining_minutes > 0:
                    day_index = (day_index + 1) % 7

        return slots

    def _next_available_time(self, existing_slots, day):
        day_slots = [s for s in existing_slots if s.day_of_week == day]
        if not day_slots:
            return DAY_START
        latest_end = max(
            datetime.combine(date.today(), s.end_time) for s in day_slots
        )
        candidate = latest_end.time()
        if candidate >= DAY_END:
            return None
        return candidate
