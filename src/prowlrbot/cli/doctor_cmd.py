"""prowlr doctor — thin wrapper around prowlr-doctor package."""
import click


@click.command("doctor")
@click.option(
    "--profile",
    default="developer",
    type=click.Choice(["developer", "security", "minimal", "agent-builder", "research"]),
    show_default=True,
    help="Recommendation profile.",
)
@click.option("--json", "as_json", is_flag=True, help="Machine-readable JSON output.")
@click.option("--write-plan", is_flag=True, help="Write fix plan to ~/.claude/doctor-plan.json.")
@click.option("--diff", is_flag=True, help="Show settings.json diff from plan on disk.")
@click.option("--apply", is_flag=True, help="Apply plan at ~/.claude/doctor-plan.json.")
@click.option("--no-tui", is_flag=True, help="Rich report only, no Textual app.")
def doctor_cmd(profile, as_json, write_plan, diff, apply, no_tui):
    """Audit your Claude Code environment for token waste and security issues."""
    try:
        from prowlr_doctor.scanner import load_snapshot, run_audit
        from prowlr_doctor.recommender import recommend
        from prowlr_doctor.patch_planner import build_plan, apply_plan
        from prowlr_doctor.reporter import render
        from prowlr_doctor import paths
    except ImportError:
        click.echo(
            "prowlr-doctor is not installed.\n"
            "Install with: pip install prowlr-doctor",
            err=True,
        )
        raise SystemExit(1)

    import json as _json
    import sys

    if apply:
        plan_path = paths.doctor_plan_path()
        if not plan_path.exists():
            click.echo(f"No plan found at {plan_path}. Run: prowlr doctor --write-plan", err=True)
            sys.exit(1)
        from prowlr_doctor.models import FixAction, PatchPlan
        data = _json.loads(plan_path.read_text())
        actions = [
            FixAction(
                action_type=a["action_type"], target=a["target"],
                settings_path=a.get("settings_path"), before=a["before"], after=a["after"],
                reversible=a.get("reversible", True), requires_restart=a.get("requires_restart", False),
            )
            for a in data.get("actions", []) if a.get("action_type") != "condense"
        ]
        plan = PatchPlan(
            version=data["version"], generated_at=data["generated_at"], profile=data["profile"],
            findings_count=data["findings_count"], actions=actions,
            estimated_savings=data["estimated_savings"], settings_diff=data["settings_diff"],
            plan_path=plan_path,
        )
        apply_plan(plan)
        click.echo(f"Applied {len(actions)} changes. Restart Claude Code to reload.")
        return

    env = load_snapshot()
    findings, budget = run_audit(env)
    rec = recommend(findings, profile)

    if as_json or write_plan:
        plan = build_plan(env, rec)
        if as_json:
            from prowlr_doctor.cli import _build_json_output
            output = _build_json_output(env, findings, budget, rec, plan)
            click.echo(_json.dumps(output, indent=2))
            paths.doctor_cache_path().write_text(_json.dumps(output, indent=2))
        if write_plan:
            paths.doctor_plan_path().write_text(plan.to_json())
            click.echo(f"Plan written to {paths.doctor_plan_path()}")
        return

    render(findings, budget, rec)
