#!/usr/bin/env python3
"""
fc.py — Freedcamp CLI for Claude Code
Usage: python src/fc.py <command> [args]

Task status: 0=not-started  1=completed  2=in-progress
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://freedcamp.com/api/v1"
API_KEY = os.getenv("FC_API_KEY", "")
API_SECRET = os.getenv("FC_API_SECRET", "")
FC_USER_ID = os.getenv("FC_USER_ID", "")

STATUS_MAP = {"open": 0, "notstarted": 0, "inprogress": 2, "done": 1, "completed": 1}
STATUS_LABEL = {0: "open", 1: "completed", 2: "in-progress"}


def _auth() -> dict:
    if not API_KEY or not API_SECRET:
        print("ERROR: FC_API_KEY and FC_API_SECRET not set. Check your .env file.", file=sys.stderr)
        sys.exit(1)
    ts = str(int(time.time()))
    sig = hmac.new(
        API_SECRET.encode("utf-8"),
        (API_KEY + ts).encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()
    return {"api_key": API_KEY, "timestamp": ts, "hash": sig}


def _get(path: str, params: dict = None, extra_pairs: list = None) -> dict:
    """GET with optional list params (e.g. status[]=0&status[]=2)."""
    p = _auth()
    if params:
        p.update(params)
    # Build request with any repeated params
    req_params = list(p.items())
    if extra_pairs:
        req_params.extend(extra_pairs)
    r = requests.get(f"{API_BASE}{path}", params=req_params, timeout=15)
    _check(r)
    return r.json()


def _post(path: str, body: dict = None) -> dict:
    p = _auth()
    r = requests.post(f"{API_BASE}{path}", params=p, json=body or {}, timeout=15)
    _check(r)
    return r.json()


def _delete(path: str) -> dict:
    p = _auth()
    r = requests.delete(f"{API_BASE}{path}", params=p, timeout=15)
    _check(r)
    return r.json()


def _check(r: requests.Response):
    try:
        r.raise_for_status()
    except requests.HTTPError:
        try:
            msg = r.json().get("msg", r.text)
        except Exception:
            msg = r.text
        print(f"ERROR {r.status_code}: {msg}", file=sys.stderr)
        sys.exit(1)
    body = r.json()
    if body.get("http_code", 200) >= 400:
        print(f"ERROR: {body.get('msg', 'unknown error')}", file=sys.stderr)
        sys.exit(1)


def _out(data):
    sys.stdout.buffer.write((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_projects(args):
    """List all projects."""
    result = _get("/projects")
    projects = result.get("data", {}).get("projects", [])
    _out([
        {
            "id": p.get("id"),
            "title": p.get("project_name"),
            "description": (p.get("project_description") or "").strip(),
            "group": p.get("group_name") or "",
            "active": p.get("f_active", True),
        }
        for p in projects
    ])


def cmd_tasks(args):
    """List tasks in a project. Default: open (not-started + in-progress). Use --status done for completed."""
    params = {"project_id": args.project_id, "limit": 200}

    if args.status:
        s = args.status.lower()
        if s in ("done", "completed"):
            extra = [("status[]", "1")]
        elif s in ("inprogress", "in-progress"):
            extra = [("status[]", "2")]
        else:
            extra = [("status[]", "0"), ("status[]", "2")]
    else:
        # Default: all active (not-started + in-progress)
        extra = [("status[]", "0"), ("status[]", "2")]

    result = _get("/tasks", params, extra_pairs=extra)
    tasks = result.get("data", {}).get("tasks", [])

    # Only top-level tasks (h_level 0); children are included under them
    top = [t for t in tasks if str(t.get("h_level", 0)) == "0"]

    _out([
        {
            "id": t.get("id"),
            "title": t.get("title"),
            "description": (t.get("description") or "").strip()[:300],
            "status": STATUS_LABEL.get(t.get("status"), t.get("status")),
            "priority": t.get("priority"),
            "list_id": t.get("task_group_id"),
            "list": t.get("task_group_name") or "",
            "due": t.get("due_ts") or "",
            "subtasks": [
                {
                    "id": s.get("id"),
                    "title": s.get("title"),
                    "status": STATUS_LABEL.get(s.get("status"), s.get("status")),
                }
                for s in (t.get("children") or [])
            ],
        }
        for t in top
    ])


def cmd_lists(args):
    """Derive task lists from a project's tasks (since lists endpoint requires specific app access)."""
    result = _get("/tasks", {"project_id": args.project_id, "limit": 200},
                  extra_pairs=[("status[]", "0"), ("status[]", "2"), ("status[]", "1")])
    tasks = result.get("data", {}).get("tasks", [])
    seen = {}
    for t in tasks:
        gid = t.get("task_group_id")
        gname = t.get("task_group_name")
        if gid and gid not in seen:
            seen[gid] = gname
    _out([{"id": k, "title": v} for k, v in seen.items()])


def cmd_create_task(args):
    """Create a task in a project."""
    body = {"project_id": args.project_id, "title": args.title}
    if args.description:
        body["description"] = args.description
    if args.list_id:
        body["task_group_id"] = args.list_id
    if args.priority:
        body["priority"] = int(args.priority)
    result = _post("/tasks", body)
    task = (result.get("data", {}).get("tasks") or [{}])[0]
    _out({"success": True, "task_id": task.get("id"), "title": args.title})


def cmd_update_task(args):
    """Update a task's status, title, description, or list.
    Status values: open (0), inprogress (2), done (1)
    """
    body = {}
    if args.title:
        body["title"] = args.title
    if args.status is not None:
        s = args.status.lower()
        body["status"] = STATUS_MAP.get(s, int(s) if s.isdigit() else 0)
    if args.description:
        body["description"] = args.description
    if args.priority:
        body["priority"] = int(args.priority)
    if args.list_id:
        body["task_group_id"] = args.list_id
    if not body:
        print("Nothing to update. Provide --title, --status, --description, or --priority")
        return
    result = _post(f"/tasks/{args.task_id}", body)
    _out({"success": True, "task_id": args.task_id, "updated": body, "msg": result.get("msg", "OK")})


def cmd_comment(args):
    """Add a comment to a task."""
    body = {
        "task_id": args.task_id,
        "item_type": "2",
        "description": args.text,
    }
    result = _post("/comments", body)
    _out({"success": True, "msg": result.get("msg", "OK")})


def cmd_create_project(args):
    """Create a new Freedcamp project."""
    body = {"project_name": args.title}
    if args.description:
        body["project_description"] = args.description
    if args.group_id:
        body["group_id"] = args.group_id
    result = _post("/projects", body)
    project = (result.get("data", {}).get("projects") or [{}])[0]
    _out({"success": True, "project_id": project.get("id"), "title": args.title})


def cmd_delete_task(args):
    """Permanently delete a task. Prefer update --status done to mark completed instead."""
    result = _delete(f"/tasks/{args.task_id}")
    _out({"success": True, "msg": result.get("msg", "OK")})


def cmd_get_times(args):
    """Fetch time records for a project, optionally filtered by date range."""
    params = {"project_id": args.project_id}
    if args.from_date:
        params["from_date"] = args.from_date
    if args.to_date:
        params["to_date"] = args.to_date
    result = _get("/times", params)
    records = result.get("data", {}).get("times", [])
    total_minutes = sum(int(r.get("minutes_count", 0)) for r in records)
    _out({
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2),
        "records": [
            {
                "id": r.get("id"),
                "task_id": r.get("link_item_id"),
                "minutes": r.get("minutes_count"),
                "date": r.get("date"),
                "description": (r.get("description") or "").strip(),
            }
            for r in records
        ],
    })


def cmd_log_time(args):
    """Log time spent on a task (Option B: report after the fact)."""
    today = time.strftime("%Y-%m-%d")
    body = {
        "project_id": args.project_id,
        "assigned_to_id": FC_USER_ID,
        "date": today,
        "minutes_count": int(args.minutes),
        "link_item_id": args.task_id,
        "link_app_id": "2",
    }
    if args.description:
        body["description"] = args.description
    result = _post("/times", body)
    record = (result.get("data", {}).get("times") or [{}])[0]
    _out({"success": True, "time_record_id": record.get("id"), "minutes": args.minutes, "task_id": args.task_id})


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Freedcamp CLI — Claude Code integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Task status: open=not-started  inprogress=in-progress  done=completed",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    sub.add_parser("projects", help="List all projects")

    p = sub.add_parser("tasks", help="List tasks (default: open+inprogress)")
    p.add_argument("project_id")
    p.add_argument("--status", help="open | inprogress | done")

    p = sub.add_parser("lists", help="List task lists/groups in a project")
    p.add_argument("project_id")

    p = sub.add_parser("create-task", help="Create a task")
    p.add_argument("project_id")
    p.add_argument("title")
    p.add_argument("--description", "-d")
    p.add_argument("--list-id", dest="list_id", help="task_group_id to assign list")
    p.add_argument("--priority", choices=["1", "2", "3"], help="1=low 2=medium 3=high")

    p = sub.add_parser("update-task", help="Update a task")
    p.add_argument("task_id")
    p.add_argument("--title")
    p.add_argument("--status", help="open | inprogress | done")
    p.add_argument("--description", "-d")
    p.add_argument("--priority", choices=["1", "2", "3"])
    p.add_argument("--list-id", dest="list_id", help="Move task to this task_group_id")

    p = sub.add_parser("comment", help="Add a comment to a task")
    p.add_argument("task_id")
    p.add_argument("text")

    p = sub.add_parser("create-project", help="Create a new project")
    p.add_argument("title")
    p.add_argument("--description", "-d")
    p.add_argument("--group-id", dest="group_id", help="Group/workspace ID to add project to")

    p = sub.add_parser("delete-task", help="Permanently delete a task")
    p.add_argument("task_id")

    p = sub.add_parser("get-times", help="Fetch time records for a project")
    p.add_argument("project_id")
    p.add_argument("--from-date", dest="from_date", help="Start date YYYY-MM-DD")
    p.add_argument("--to-date", dest="to_date", help="End date YYYY-MM-DD")

    p = sub.add_parser("log-time", help="Log time spent on a task")
    p.add_argument("task_id", help="Task ID the time is logged against")
    p.add_argument("minutes", type=int, help="Minutes spent")
    p.add_argument("project_id", help="Project ID the task belongs to")
    p.add_argument("--description", "-d", help="Optional note (e.g. what was done)")

    args = parser.parse_args()

    commands = {
        "projects": cmd_projects,
        "tasks": cmd_tasks,
        "lists": cmd_lists,
        "create-task": cmd_create_task,
        "update-task": cmd_update_task,
        "comment": cmd_comment,
        "create-project": cmd_create_project,
        "delete-task": cmd_delete_task,
        "get-times": cmd_get_times,
        "log-time": cmd_log_time,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
