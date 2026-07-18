"""Console demo of the career engine -- no server needed.

    python demo.py
"""

from __future__ import annotations

from app.dashboard import build_dashboard
from app.engine import analyze
from app.roadmap import generate_roadmap
from app.samples import backend_sem3_student
from app.store import ProfileStore


def main() -> None:
    profile = backend_sem3_student()
    g = profile.academic
    print("=" * 68)
    print("AI CAREER ROADMAP ENGINE  |  demo")
    print("=" * 68)
    print(
        f"Student: sem {g.current_semester}, tier {g.college_tier}, "
        f"CGPA {g.cgpa}  ->  target: {profile.goals.target_role.value.upper()}"
    )
    print(f"Study time: {profile.constraints.daily_study_hours} h/day\n")

    result = analyze(profile)
    print(f"Current readiness:   {result.readiness_pct}%")
    print(
        f"Projected readiness: {result.projected_readiness_pct}%  "
        f"(after: {', '.join(result.projected_from) or 'n/a'})\n"
    )

    print("Highest-ROI next steps")
    print("-" * 68)
    for i, rec in enumerate(result.recommendations, 1):
        tag = f"  [blocked by {', '.join(rec.blocked_by)}]" if rec.blocked_by else ""
        print(
            f"{i}. {rec.name:<24} +{rec.readiness_gain:>4} pts  "
            f"~{rec.effort_hours}h{tag}"
        )
        print(f"     {rec.reason}")

    print("\nSemester-aware roadmap")
    print("-" * 68)
    roadmap = generate_roadmap(profile)
    for sem in roadmap.semesters:
        print(f"\n  Semester {sem.semester} - {sem.theme}  "
              f"(~{sem.total_effort_hours}h)")
        for item in sem.items:
            print(f"    - {item.name} (~{item.effort_hours}h)")

    _continuous_update_demo(profile)


def _continuous_update_demo(profile) -> None:
    """Show the 'Google Maps for careers' loop: progress -> auto-recompute."""
    print("\n" + "=" * 68)
    print("CONTINUOUS UPDATE  |  progress recomputes the whole plan")
    print("=" * 68)

    store = ProfileStore(":memory:")
    sid = store.create_student(profile)

    def snapshot(label: str) -> None:
        dash = build_dashboard(sid, store.get_profile(sid),
                               store.get_completed_milestones(sid))
        wk = dash.weekly_plan[0] if dash.weekly_plan else None
        print(
            f"  {label:<28} readiness {dash.readiness.readiness_pct:>5}%   "
            f"milestones {dash.milestones.completion_pct:>5}%   "
            f"next week: {wk.focus_skill if wk else 'done'}"
        )

    snapshot("start")
    store.set_skill_level(sid, "linux", 4);  snapshot("learned Linux")
    store.set_skill_level(sid, "sql", 4);    snapshot("learned SQL")
    store.set_skill_level(sid, "apis", 4);   snapshot("learned APIs")
    store.set_milestone(sid, "github_created", True)
    store.set_milestone(sid, "resume_ready", True)
    snapshot("github + resume done")
    print()


if __name__ == "__main__":
    main()
