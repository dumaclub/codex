import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


REPO = Path(r"E:\Study\Codex")
CODEX = Path(r"C:\Users\dumaclub\.codex")
SESSION_INDEX = CODEX / "session_index.jsonl"
GLOBAL_STATE = CODEX / ".codex-global-state.json"
SESSIONS_DIR = CODEX / "sessions"

INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
DATA_IMAGE = re.compile(
    r"data:image/[a-zA-Z0-9.+-]+;base64,[a-zA-Z0-9+/=\r\n]+",
    re.IGNORECASE,
)


def read_jsonl(path):
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line_no, line in enumerate(stream, 1):
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def sanitize_text(text):
    return DATA_IMAGE.sub("[base64 image omitted]", text).rstrip()


def filename_part(text, max_length=140):
    text = INVALID_FILENAME.sub("_", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return (text or "Untitled")[:max_length].rstrip(" .")


def load_titles():
    titles = {}
    for item in read_jsonl(SESSION_INDEX):
        session_id = item.get("id")
        if session_id:
            titles[session_id] = {
                "title": item.get("thread_name") or "Untitled",
                "updatedAt": item.get("updated_at"),
            }
    return titles


def load_workspace_map():
    state = json.loads(GLOBAL_STATE.read_text(encoding="utf-8"))
    labels = state.get("electron-workspace-root-labels", {})
    local_projects = state.get("local-projects", {})
    thread_assignments = state.get("thread-project-assignments", {})

    workspace_map = {}
    saved = []

    def remember(root, project, source):
        if not root:
            return
        normalized = os.path.normcase(os.path.normpath(root))
        if normalized in workspace_map:
            return
        workspace_map[normalized] = project
        saved.append({"cwd": root, "project": project, "labelSource": source})

    for root in state.get("electron-saved-workspace-roots", []):
        project = labels.get(root) or Path(root).name
        source = (
            "electron-workspace-root-labels"
            if root in labels
            else "workspace basename"
        )
        remember(root, project, source)

    project_names = {}
    for project_id, project_info in local_projects.items():
        root_paths = project_info.get("rootPaths") or []
        project_name = project_info.get("name") or project_id
        project_names[project_id] = project_name
        for root in root_paths:
            remember(root, labels.get(root) or project_name, "local-projects")

    assignment_map = {}
    for session_id, assignment in thread_assignments.items():
        project_id = assignment.get("projectId")
        cwd = assignment.get("cwd")
        project = labels.get(cwd) or project_names.get(project_id)
        if project:
            assignment_map[session_id] = {
                "cwd": cwd,
                "project": project,
                "labelSource": "thread-project-assignments",
            }

    return workspace_map, assignment_map, saved


def extract_session(path, title_info, workspace_map, assignment_map):
    meta = None
    messages = []
    latest_timestamp = None
    for item in read_jsonl(path):
        timestamp = item.get("timestamp")
        if timestamp:
            latest_timestamp = timestamp
        if item.get("type") == "session_meta" and meta is None:
            payload = item.get("payload") or {}
            meta = {
                "id": payload.get("id"),
                "startedAt": payload.get("timestamp") or timestamp,
                "cwd": payload.get("cwd"),
            }
            continue
        if item.get("type") != "response_item":
            continue
        payload = item.get("payload") or {}
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            continue
        parts = []
        for content in payload.get("content") or []:
            if content.get("type") in {"input_text", "output_text"}:
                text = content.get("text")
                if isinstance(text, str):
                    text = sanitize_text(text)
                    if text:
                        parts.append(text)
        if parts:
            messages.append({"role": role, "text": "\n\n".join(parts)})
    if not meta or not meta["id"] or not meta["cwd"]:
        return None
    assignment = assignment_map.get(meta["id"], {})
    normalized_cwd = os.path.normcase(os.path.normpath(assignment.get("cwd") or meta["cwd"]))
    project = assignment.get("project") or workspace_map.get(normalized_cwd)
    if not project:
        return None
    info = title_info.get(meta["id"], {})
    updated_at = info.get("updatedAt") or latest_timestamp or meta["startedAt"]
    return {
        **meta,
        "project": project,
        "title": info.get("title") or "Untitled",
        "updatedAt": updated_at,
        "messages": messages,
    }


def iso_sort_value(value):
    return value or ""


def archive_filename(session):
    stamp = datetime.fromisoformat(
        session["updatedAt"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)
    return (
        f"{stamp:%Y-%m-%d_%H%M}_{filename_part(session['title'])}_"
        f"{session['id'][:8]}.md"
    )


def render_session(session):
    lines = [
        f"# {session['title']}",
        "",
        f"- Project: {session['project']}",
        f"- Session ID: `{session['id']}`",
        f"- Workspace: `{session['cwd']}`",
        f"- Started: {session['startedAt']}",
        f"- Updated: {session['updatedAt']}",
        f"- Messages exported: {len(session['messages'])}",
        "",
        "> Export note: internal system/developer instructions, tool execution logs, and base64 image payloads are omitted. Only user/assistant messages are archived.",
        "",
        "## Conversation",
        "",
    ]
    for message in session["messages"]:
        lines.extend(
            [
                f"### {'User' if message['role'] == 'user' else 'Assistant'}",
                "",
                message["text"],
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def relative_link(path):
    return quote(path.as_posix(), safe="/()[]'._-")


def main():
    title_info = load_titles()
    workspace_map, assignment_map, saved_workspaces = load_workspace_map()
    sessions = []
    for path in SESSIONS_DIR.rglob("*.jsonl"):
        session = extract_session(path, title_info, workspace_map, assignment_map)
        if session and session["messages"]:
            sessions.append(session)
    sessions.sort(key=lambda item: (item["project"], iso_sort_value(item["updatedAt"]), item["id"]))

    projects = {item["project"]: [] for item in saved_workspaces}
    for session in sessions:
        session["file"] = (
            Path("projects") / session["project"] / archive_filename(session)
        )
        projects.setdefault(session["project"], []).append(session)

    expected = {session["file"].as_posix() for session in sessions}
    for project in projects:
        project_dir = REPO / "projects" / project
        project_dir.mkdir(parents=True, exist_ok=True)
        for old_file in project_dir.glob("*.md"):
            relative = old_file.relative_to(REPO).as_posix()
            if relative not in expected:
                old_file.unlink()
    for session in sessions:
        target = REPO / session["file"]
        target.write_text(render_session(session), encoding="utf-8", newline="\n")

    exported_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    index_projects = {}
    for project, project_sessions in projects.items():
        index_projects[project] = [
            {
                "id": session["id"],
                "title": session["title"],
                "cwd": session["cwd"],
                "startedAt": session["startedAt"],
                "updatedAt": session["updatedAt"],
                "messages": len(session["messages"]),
                "file": session["file"].as_posix(),
            }
            for session in project_sessions
        ]
    totals = {
        "projects": len(projects),
        "threads": len(sessions),
        "messages": sum(len(session["messages"]) for session in sessions),
    }
    index = {
        "exportedAt": exported_at,
        "source": {
            "sessionIndex": str(SESSION_INDEX),
            "globalState": str(GLOBAL_STATE),
            "sessionsDir": str(SESSIONS_DIR),
        },
        "savedWorkspaces": saved_workspaces,
        "totals": totals,
        "projects": index_projects,
    }
    (REPO / "archive-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    readme = [
        "# Codex Conversation Archive",
        "",
        f"Exported: {exported_at}",
        "",
        "This repository stores project conversation archives from Codex as Markdown files. It does not include source projects or the raw `.codex` folder.",
        "",
        "## Scope",
        "",
    ]
    for workspace in saved_workspaces:
        project = workspace["project"]
        project_sessions = projects.get(project, [])
        count = sum(len(session["messages"]) for session in project_sessions)
        readme.append(
            f"- {project}: {len(project_sessions)} threads, {count} user/assistant messages"
        )
    readme.extend(
        [
            f"- Total: {totals['threads']} threads, {totals['messages']} user/assistant messages",
            "",
            "## File Structure",
            "",
        ]
    )
    for workspace in saved_workspaces:
        project = workspace["project"]
        readme.append(f"- `projects/{project}/`: {project} conversations")
    readme.extend(
        [
            "- `conversation.md`: earlier Git-upload check thread kept for reference",
            "- `archive-index.json`: machine-readable export index",
            "",
            "## Safety Note",
            "",
            r"The raw `C:\Users\dumaclub\.codex` folder is not uploaded because it can contain auth, logs, cache, and other sensitive app data.",
            "",
            "Each Markdown file omits internal system/developer instructions, tool execution logs, and base64 image payloads. User/assistant messages are preserved.",
            "",
            "## Conversations",
            "",
        ]
    )
    for workspace in saved_workspaces:
        project = workspace["project"]
        readme.extend([f"### {project}", ""])
        for session in projects.get(project, []):
            stamp = session["updatedAt"][:10]
            readme.append(
                f"- {stamp} [{session['title']}]({relative_link(session['file'])})"
            )
        readme.append("")
    (REPO / "README.md").write_text(
        "\n".join(readme).rstrip() + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(totals, ensure_ascii=False))
    for project, project_sessions in projects.items():
        print(
            f"{project}: {len(project_sessions)} threads, "
            f"{sum(len(item['messages']) for item in project_sessions)} messages"
        )


if __name__ == "__main__":
    main()
