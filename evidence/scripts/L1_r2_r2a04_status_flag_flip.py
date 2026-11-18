"""R2A-04: editing a status row's is_closed flag. The TaskStatus post_save handler only re-evaluates
user stories; tasks keep finished_date=None (burndown) and a sprint whose items are US-less tasks
is not closed. IssueStatus has no handler at all: issues keep finished_date=None and the sprint
is not re-evaluated."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
tss = {s["slug"]: s for s in P["task_statuses"]}; iss = {s["slug"]: s for s in P["issue_statuses"]}
pts = {p["value"]: p["id"] for p in P["points"]}; role = [r for r in P["roles"] if r["computable"]][0]
def g(path): return owner.get(path).json()
def mk_ms(n): return owner.post("/milestones", {"project": pid, "name": n, "estimated_start": "2026-11-01", "estimated_finish": "2026-11-30"}).json()

m1 = mk_ms("m1"); m2 = mk_ms("m2"); m3 = mk_ms("m3")
us = owner.post("/userstories", {"project": pid, "subject": "a", "milestone": m1["id"], "points": {str(role["id"]): pts[8.0]}}).json()
t = owner.post("/tasks", {"project": pid, "subject": "t", "user_story": us["id"], "status": tss["ready-for-test"]["id"]}).json()
t2 = owner.post("/tasks", {"project": pid, "subject": "t2 (no US)", "milestone": m2["id"], "status": tss["ready-for-test"]["id"]}).json()
i = owner.post("/issues", {"project": pid, "subject": "i", "milestone": m3["id"], "status": iss["needs-info"]["id"]}).json()

print("PATCH task-status 'ready-for-test' is_closed=true ->", owner.patch(f"/task-statuses/{tss['ready-for-test']['id']}", {"is_closed": True}).status_code)
tt = g(f"/tasks/{t['id']}")
print(f"task in US: is_closed={tt['is_closed']} finished_date={tt['finished_date']}; US is_closed={g('/userstories/%d' % us['id'])['is_closed']}; sprint m1 closed={g('/milestones/%d' % m1['id'])['closed']}")
st = g(f"/milestones/{m1['id']}/stats")
print(f"sprint m1 burndown: total_points={st['total_points']} completed_userstories={st['completed_userstories']} completed_tasks={st['completed_tasks']} open_points on last day={st['days'][-1]['open_points']}")
print(f"sprint m2 (one US-less task, now closed): task is_closed={g('/tasks/%d' % t2['id'])['is_closed']} milestone.closed={g('/milestones/%d' % m2['id'])['closed']}")

print("PATCH issue-status 'needs-info' is_closed=true ->", owner.patch(f"/issue-statuses/{iss['needs-info']['id']}", {"is_closed": True}).status_code)
ii = g(f"/issues/{i['id']}")
print(f"issue: is_closed={ii['is_closed']} finished_date={ii['finished_date']}; sprint m3 closed={g('/milestones/%d' % m3['id'])['closed']}")
ist = g(f"/projects/{pid}/issues_stats")
print(f"issues_stats: closed_issues={ist['closed_issues']} but closed today in by_open_closed={ist['last_four_weeks_days']['by_open_closed']['closed'][-1]}")

print("control (single edit): ", end="")
t3 = owner.post("/tasks", {"project": pid, "subject": "t3", "milestone": mk_ms("m4")["id"], "status": tss["new"]["id"]}).json()
t3 = owner.patch(f"/tasks/{t3['id']}", {"status": tss["closed"]["id"], "version": t3["version"]}).json()
print(f"task finished_date set={t3['finished_date'] is not None}, milestone.closed={g('/milestones/%d' % t3['milestone'])['closed']}")
