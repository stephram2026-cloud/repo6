"""R2A-11 / R2A-12: write routes that skip the blocked-project and archived-project guards.
Usage: python3 r2a11_blocked_archived_bypass.py blocked|archived
The project flag is set the way staff do it (Django admin field), here through the Django shell."""
import sys, requests
from lib import *
mode = sys.argv[1]  # archived | blocked
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
owner.patch(f"/projects/{pid}", {"is_epics_activated": True})
m1 = owner.post("/milestones", {"project": pid, "name": "m1", "estimated_start": "2026-11-01", "estimated_finish": "2026-11-30"}).json()
m2 = owner.post("/milestones", {"project": pid, "name": "m2", "estimated_start": "2026-12-01", "estimated_finish": "2026-12-30"}).json()
us = owner.post("/userstories", {"project": pid, "subject": "us"}).json()
us2 = owner.post("/userstories", {"project": pid, "subject": "us2"}).json()
t = owner.post("/tasks", {"project": pid, "subject": "t"}).json()
i = owner.post("/issues", {"project": pid, "subject": "i"}).json()
e = owner.post("/epics", {"project": pid, "subject": "e"}).json()
w = owner.post("/wiki", {"project": pid, "slug": "home", "content": "x"}).json()
ca = owner.post("/userstory-custom-attributes", {"project": pid, "name": "f", "type": "text"}).json()
if mode == "archived":
    djshell(f"from taiga.projects.models import Project; Project.objects.filter(id={pid}).update(archived_code='archived-by-staff')")
else:
    djshell(f"from taiga.projects.models import Project; Project.objects.filter(id={pid}).update(blocked_code='blocked-by-staff')")
p = owner.get(f"/projects/{pid}").json(); print("project archived_code", p.get("archived_code"), "blocked_code", p.get("blocked_code"))
uss = P["us_statuses"]; role = P["roles"][0]
up = requests.Session(); up.headers["Authorization"] = owner.s.headers["Authorization"]
tests = [
 ("control: POST /userstories", lambda: owner.post("/userstories", {"project": pid, "subject": "x"})),
 ("control: PATCH /userstories/id", lambda: owner.patch(f"/userstories/{us['id']}", {"subject": "y", "version": 1})),
 ("control: DELETE /userstories/id", lambda: owner.delete(f"/userstories/{us2['id']}")),
 ("userstories/bulk_create", lambda: owner.post("/userstories/bulk_create", {"project_id": pid, "bulk_stories": "a\nb"})),
 ("tasks/bulk_create", lambda: owner.post("/tasks/bulk_create", {"project_id": pid, "bulk_tasks": "a\nb"})),
 ("issues/bulk_create", lambda: owner.post("/issues/bulk_create", {"project_id": pid, "bulk_issues": "a\nb"})),
 ("epics/bulk_create", lambda: owner.post("/epics/bulk_create", {"project_id": pid, "bulk_epics": "a\nb"})),
 ("epics/id/related_userstories/bulk_create", lambda: owner.post(f"/epics/{e['id']}/related_userstories/bulk_create", {"project_id": pid, "bulk_userstories": "a\nb"})),
 ("userstories/bulk_update_backlog_order", lambda: owner.post("/userstories/bulk_update_backlog_order", {"project_id": pid, "bulk_userstories": [us["id"]], "milestone_id": m1["id"]})),
 ("userstories/bulk_update_kanban_order", lambda: owner.post("/userstories/bulk_update_kanban_order", {"project_id": pid, "bulk_userstories": [us["id"]], "status_id": uss[-2]["id"]})),
 ("userstories/bulk_update_milestone", lambda: owner.post("/userstories/bulk_update_milestone", {"project_id": pid, "milestone_id": m2["id"], "bulk_stories": [{"us_id": us["id"], "order": 1}]})),
 ("tasks/bulk_update_milestone", lambda: owner.post("/tasks/bulk_update_milestone", {"project_id": pid, "milestone_id": m2["id"], "bulk_tasks": [{"task_id": t["id"], "order": 1}]})),
 ("issues/bulk_update_milestone", lambda: owner.post("/issues/bulk_update_milestone", {"project_id": pid, "milestone_id": m2["id"], "bulk_issues": [{"issue_id": i["id"]}]})),
 ("tasks/bulk_update_taskboard_order", lambda: owner.post("/tasks/bulk_update_taskboard_order", {"project_id": pid, "bulk_tasks": [{"task_id": t["id"], "order": 5}]})),
 ("milestones/id/move_userstories_to_sprint", lambda: owner.post(f"/milestones/{m2['id']}/move_userstories_to_sprint", {"project_id": pid, "milestone_id": m1["id"], "bulk_stories": [{"us_id": us["id"], "order": 1}]})),
 ("milestones/id/move_issues_to_sprint", lambda: owner.post(f"/milestones/{m2['id']}/move_issues_to_sprint", {"project_id": pid, "milestone_id": m1["id"], "bulk_issues": [{"issue_id": i["id"], "order": 1}]})),
 ("issues/id/promote_to_user_story", lambda: owner.post(f"/issues/{i['id']}/promote_to_user_story", {"project_id": pid})),
 ("tasks/id/promote_to_user_story", lambda: owner.post(f"/tasks/{t['id']}/promote_to_user_story", {"project_id": pid})),
 ("userstories/id/upvote", lambda: owner.post(f"/userstories/{us['id']}/upvote")),
 ("userstories/id/watch", lambda: owner.post(f"/userstories/{us['id']}/watch")),
 ("projects/id/like", lambda: owner.post(f"/projects/{pid}/like")),
 ("projects/id/create_tag", lambda: owner.post(f"/projects/{pid}/create_tag", {"tag": "newtag", "color": "#ff0000"})),
 ("userstory-statuses/bulk_update_order", lambda: owner.post("/userstory-statuses/bulk_update_order", {"project": pid, "bulk_userstory_statuses": [[uss[0]["id"], 9], [uss[1]["id"], 1]]})),
 ("memberships/bulk_create", lambda: owner.post("/memberships/bulk_create", {"project_id": pid, "bulk_memberships": [{"role_id": role["id"], "username": "nobody%s@example.com" % pid}]})),
 ("userstories/attachments POST", lambda: up.post(BASE + "/userstories/attachments", data={"project": pid, "object_id": us["id"]}, files={"attached_file": ("a.txt", b"x")})),
 ("userstories/custom-attributes-values PATCH", lambda: owner.patch(f"/userstories/custom-attributes-values/{us['id']}", {"attributes_values": {str(ca["id"]): "v"}, "version": 1})),
 ("wiki PATCH", lambda: owner.patch(f"/wiki/{w['id']}", {"content": "changed", "version": 1})),
 ("userstory-custom-attributes POST", lambda: owner.post("/userstory-custom-attributes", {"project": pid, "name": "g", "type": "text"})),
 ("webhooks POST", lambda: owner.post("/webhooks", {"project": pid, "name": "wh", "url": "http://example.com/x", "key": "k"})),
 ("projects/id/transfer_request", lambda: owner.post(f"/projects/{pid}/transfer_request")),
 ("projects/id/leave", lambda: owner.post(f"/projects/{pid}/leave")),
 ("projects/id/create_template", lambda: owner.post(f"/projects/{pid}/create_template", {"template_name": "x", "template_description": "y"})),
 ("userstory-due-dates POST", lambda: owner.post("/userstory-due-dates", {"project": pid, "name": "dd", "days_to_due": 3, "color": "#000000"})),
 ("task-due-dates POST", lambda: owner.post("/task-due-dates", {"project": pid, "name": "dd", "days_to_due": 3, "color": "#000000"})),
]
for name, fn in tests:
    r = fn(); print(f"{r.status_code}  {name}  {r.text[:90] if r.status_code >= 400 else ''}")

print("--- state after the calls (project is %s) ---" % mode)
print("issue still exists:", owner.get(f"/issues/{i['id']}").status_code, "| task still exists:", owner.get(f"/tasks/{t['id']}").status_code)
u = owner.get(f"/userstories/{us['id']}").json(); print("story 'us' milestone:", u["milestone"], "(was None)")
print("user stories in project:", len(owner.get(f"/userstories?project={pid}").json()), "(was 2)")
