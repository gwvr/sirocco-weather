"""One-off script to migrate beads issues to tk tickets."""
import json
import subprocess

ISSUES_FILE = ".beads/backup/issues.jsonl"

with open(ISSUES_FILE) as f:
    issues = [json.loads(l) for l in f if l.strip()]

print(f"Migrating {len(issues)} issues...")

for issue in issues:
    args = [
        "tk", "create", issue["title"],
        "-t", issue["issue_type"],
        "-p", str(issue["priority"]),
        "--external-ref", issue["id"],
    ]
    if issue.get("description"):
        args += ["-d", issue["description"]]
    if issue.get("assignee"):
        args += ["-a", issue["assignee"]]
    if issue.get("design"):
        args += ["--design", issue["design"]]
    if issue.get("acceptance_criteria"):
        args += ["--acceptance", issue["acceptance_criteria"]]

    result = subprocess.run(args, capture_output=True, text=True, check=True)
    new_id = result.stdout.strip()
    print(f"  {issue['id']} -> {new_id} [{issue['status']}]: {issue['title'][:60]}")

    status = issue["status"]
    if status == "closed":
        subprocess.run(["tk", "close", new_id], check=True)
    elif status == "in_progress":
        subprocess.run(["tk", "start", new_id], check=True)
    elif status == "deferred":
        subprocess.run(
            ["tk", "add-note", new_id, "Originally deferred in beads"],
            check=True,
        )

    if issue.get("notes"):
        subprocess.run(["tk", "add-note", new_id, issue["notes"]], check=True)

print("Done.")
