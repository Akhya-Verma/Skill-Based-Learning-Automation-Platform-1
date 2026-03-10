import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config.settings import HOURS_PER_WEEK

_DIFFICULTY_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}


def generate_learning_path(missing_skills, optional_gaps, recommendations):

    # Build ordered task list
    tasks = []
    for skill in missing_skills:
        for module in recommendations.get(skill, []):
            tasks.append({"priority": 0, "skill": skill, "module": module})
    for skill in optional_gaps:
        for module in recommendations.get(skill, []):
            tasks.append({"priority": 1, "skill": skill, "module": module})

    # Sort by priority then difficulty
    tasks.sort(key=lambda t: (
        t["priority"],
        _DIFFICULTY_ORDER.get(t["module"].get("difficulty", "beginner"), 1)
    ))

    # Pack into weeks
    weeks = []
    week_num = 1
    remaining = HOURS_PER_WEEK
    cur_modules, cur_skills, cur_hours = [], [], 0
    total_hours = 0

    for task in tasks:
        module     = task["module"]
        skill      = task["skill"]
        hours_left = float(module.get("hours") or 10)

        while hours_left > 0:
            allot       = min(hours_left, remaining)
            hours_left -= allot
            remaining  -= allot
            cur_hours  += allot
            total_hours += allot

            if skill not in cur_skills:
                cur_skills.append(skill)

            cur_modules.append({**module, "hours_this_week": round(allot, 1)})

            if remaining <= 0:
                weeks.append(_make_week(week_num, cur_skills, cur_modules, cur_hours))
                week_num += 1
                remaining = HOURS_PER_WEEK
                cur_modules, cur_skills, cur_hours = [], [], 0

    # Flush last partial week
    if cur_modules:
        weeks.append(_make_week(week_num, cur_skills, cur_modules, cur_hours))

    if not weeks:
        weeks = [{
            "week": 1,
            "theme": "No gaps — you are ready!",
            "skills": [],
            "modules": [],
            "estimated_hours": 0
        }]

    return {
        "total_weeks": len(weeks),
        "total_hours": round(total_hours, 1),
        "weeks":       weeks,
    }


def _make_week(num, skills, modules, hours):
    return {
        "week":            num,
        "theme":           _theme(num, skills),
        "skills":          list(dict.fromkeys(skills)),
        "modules":         modules,
        "estimated_hours": round(hours, 1),
    }


def _theme(week_num, skills):
    if not skills:
        return f"Week {week_num}"
    if len(skills) == 1:
        return f"{skills[0]} Fundamentals" if week_num <= 2 else f"Advanced {skills[0]}"
    return " & ".join(skills[:2]) + (" +" if len(skills) > 2 else "")