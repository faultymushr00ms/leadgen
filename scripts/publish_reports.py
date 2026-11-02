#!/usr/bin/env python3
"""Publish data/reports onto origin's reports branch.

Uses a separate clone at ~/.forge-reports so the project working tree and
the current branch are not touched. Credentials come from the existing git
credential helper (osxkeychain on the Mac). Embedded userinfo is stripped
from the origin URL before it is stored or logged. Push failures are logged
and returned; they do not raise.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ORIGIN = "https://github.com/faultymushr00ms/leadgen.git"
ALLOWED_RE = re.compile(
    r"^(?:audit_\d{4}-\d{2}-\d{2}\.(?:md|json)|scan_\d{4}-\d{2}-\d{2}\.(?:md|json)|latest\.md)$"
)
USERINFO_RE = re.compile(r"^(https?://)(?:[^/@\s]+)@", re.IGNORECASE)
SECRET_RE = re.compile(
    r"(https?://)(?:[^/@\s]+)@|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|x-access-token[:\s=]+\S+",
    re.IGNORECASE,
)
BRANCH_README = """# FORGE daily reports

Generated scan and audit reports for the FORGE sales desk.

Open [data/reports/latest.md](data/reports/latest.md).

This branch is updated by `scripts/nightly_scan.sh`. It is not the application source.
"""


class PublishError(Exception):
    pass


def sanitize_origin(url: str) -> str:
    """Drop https userinfo so a token in `git remote get-url` is not stored."""
    return USERINFO_RE.sub(r"\1", url.strip())


def sanitize_text(text: str) -> str:
    cleaned = SECRET_RE.sub(
        lambda match: match.group(1) if match.group(1) else "[redacted]",
        text or "",
    )
    return cleaned.strip()


def git_env() -> dict:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "Never"
    return env


def run_git(dest: Path, *args: str, env: dict, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(dest), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    if check and proc.returncode != 0:
        detail = sanitize_text(proc.stderr or proc.stdout or "git failed")
        raise PublishError(detail or "git failed")
    return proc


def resolve_origin(project_dir: str, env: dict | None = None) -> str:
    env = env or git_env()
    try:
        proc = subprocess.run(
            ["git", "-C", project_dir, "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
    except OSError:
        return DEFAULT_ORIGIN
    if proc.returncode != 0 or not proc.stdout.strip():
        return DEFAULT_ORIGIN
    return sanitize_origin(proc.stdout.strip())


def assert_outside_project(project: Path, dest: Path) -> None:
    project = project.resolve()
    dest = dest.resolve()
    if dest == project or project in dest.parents:
        raise PublishError("refusing to publish inside the project working tree")


def report_names(reports_dir: Path) -> list[str]:
    if not reports_dir.is_dir():
        return []
    return sorted(name for name in os.listdir(reports_dir) if ALLOWED_RE.fullmatch(name))


def render_latest(as_of: str, names: list[str]) -> str:
    today = [name for name in names if as_of in name and name != "latest.md"]
    lines = [
        "# Latest FORGE reports",
        "",
        f"Run date: {as_of}",
        "",
        "Today's files:",
        "",
    ]
    if not today:
        lines.append("- (none)")
    else:
        for name in today:
            lines.append(f"- [{name}]({name})")
    lines.extend([
        "",
        "Older dated reports stay on this branch.",
        "",
    ])
    return "\n".join(lines)


def write_latest(reports_dir: Path, as_of: str) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    names = [name for name in report_names(reports_dir) if name != "latest.md"]
    (reports_dir / "latest.md").write_text(render_latest(as_of, names), encoding="utf-8")


def ensure_repo(dest: Path, origin: str, env: dict) -> None:
    if dest.exists() and not dest.is_dir():
        raise PublishError(f"{dest} exists and is not a directory")
    if dest.exists() and any(dest.iterdir()) and not (dest / ".git").exists():
        raise PublishError(f"{dest} is not a git clone; refusing to replace it")
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        proc = subprocess.run(
            ["git", "init", "-b", "reports", str(dest)],
            capture_output=True,
            text=True,
            env=env,
        )
        if proc.returncode != 0:
            raise PublishError(sanitize_text(proc.stderr or proc.stdout or "git init failed"))
    current = run_git(dest, "remote", "get-url", "origin", env=env, check=False)
    if current.returncode != 0:
        run_git(dest, "remote", "add", "origin", origin, env=env)
        return
    if sanitize_origin(current.stdout) != origin:
        run_git(dest, "remote", "set-url", "origin", origin, env=env)


def _on_reports_branch(dest: Path, env: dict) -> bool:
    current = run_git(dest, "symbolic-ref", "--short", "HEAD", env=env, check=False)
    return current.returncode == 0 and current.stdout.strip() == "reports"


def _has_reports_commit(dest: Path, env: dict) -> bool:
    probed = run_git(dest, "rev-parse", "--verify", "refs/heads/reports", env=env, check=False)
    return probed.returncode == 0


def sync_reports_branch(dest: Path, env: dict) -> None:
    fetched = run_git(dest, "fetch", "--depth", "1", "origin", "reports", env=env, check=False)
    remote_ok = fetched.returncode == 0
    local_ok = _has_reports_commit(dest, env)
    if not remote_ok:
        message = sanitize_text(fetched.stderr or fetched.stdout or "fetch failed")
        print(f"[publish] fetch reports: {message or 'failed'}")
    if remote_ok and local_ok:
        run_git(dest, "checkout", "reports", env=env)
        rebase = run_git(dest, "rebase", "FETCH_HEAD", env=env, check=False)
        if rebase.returncode != 0:
            print("[publish] rebase onto origin/reports failed; resetting to origin and copying local reports")
            run_git(dest, "rebase", "--abort", env=env, check=False)
            run_git(dest, "reset", "--hard", "FETCH_HEAD", env=env)
        return
    if remote_ok:
        run_git(dest, "checkout", "-B", "reports", "FETCH_HEAD", env=env)
        return
    if not _on_reports_branch(dest, env):
        run_git(dest, "checkout", "--orphan", "reports", env=env)
        run_git(dest, "rm", "-rf", ".", env=env, check=False)


def copy_reports(reports_dir: Path, dest: Path) -> int:
    target = dest / "data" / "reports"
    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in report_names(reports_dir):
        source = reports_dir / name
        (target / name).write_bytes(source.read_bytes())
        copied += 1
    return copied


def ensure_identity(dest: Path, env: dict) -> None:
    email = run_git(dest, "config", "--get", "user.email", env=env, check=False)
    if email.returncode == 0 and email.stdout.strip():
        return
    run_git(dest, "config", "user.email", "forge-reports@localhost", env=env)
    run_git(dest, "config", "user.name", "FORGE reports", env=env)


def commit_reports(dest: Path, as_of: str, env: dict) -> bool:
    ensure_identity(dest, env)
    run_git(dest, "add", "--", "data/reports", "README.md", env=env)
    diff = run_git(dest, "diff", "--cached", "--quiet", env=env, check=False)
    if diff.returncode == 0:
        return False
    if diff.returncode != 1:
        raise PublishError(sanitize_text(diff.stderr or diff.stdout or "git diff failed"))
    run_git(
        dest,
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-m",
        f"Reports {as_of}",
        env=env,
    )
    return True


def push_reports(dest: Path, env: dict) -> None:
    proc = run_git(dest, "push", "origin", "HEAD:reports", env=env, check=False)
    if proc.returncode != 0:
        raise PublishError(sanitize_text(proc.stderr or proc.stdout or "push failed"))


def publish(project_dir: str, reports_dir: str, dest_dir: str, origin_url: str, as_of: str) -> int:
    env = git_env()
    project = Path(project_dir)
    reports = Path(reports_dir)
    dest = Path(dest_dir)
    origin = sanitize_origin(origin_url)
    try:
        assert_outside_project(project, dest)
        write_latest(reports, as_of)
        if not report_names(reports):
            print("[publish] no report files to publish")
            return 0
        ensure_repo(dest, origin, env)
        sync_reports_branch(dest, env)
        copied = copy_reports(reports, dest)
        (dest / "README.md").write_text(BRANCH_README, encoding="utf-8")
        committed = commit_reports(dest, as_of, env)
        if not committed:
            print(f"[publish] no new report files ({copied} already on the branch)")
        push_reports(dest, env)
    except PublishError as exc:
        print(f"[publish] FAILED: {exc}")
        return 1
    except Exception as exc:
        print(f"[publish] FAILED: {sanitize_text(str(exc))}")
        return 1
    print(f"[publish] pushed {origin} branch reports ({as_of})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Publish data/reports to the reports branch.")
    parser.add_argument("--project", default=ROOT)
    parser.add_argument("--reports", default=os.path.join(ROOT, "data", "reports"))
    parser.add_argument("--dest", default=str(Path.home() / ".forge-reports"))
    parser.add_argument("--origin", default=None)
    parser.add_argument("--date", default=None, help="Run date YYYY-MM-DD. Default: today.")
    args = parser.parse_args(argv)
    if args.date:
        try:
            as_of = date.fromisoformat(args.date).isoformat()
        except ValueError:
            print("invalid --date, expected YYYY-MM-DD", file=sys.stderr)
            return 1
    else:
        as_of = date.today().isoformat()
    origin = args.origin or resolve_origin(args.project)
    return publish(args.project, args.reports, args.dest, origin, as_of)


if __name__ == "__main__":
    sys.exit(main())
