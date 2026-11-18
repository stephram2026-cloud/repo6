"""R2A-03: deleting a status with ?moveTo=<other status> moves the rows with queryset.update(),
so nothing derived from the status is recomputed (US is_closed/finish_date, task/issue
finished_date, milestone closed)."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
uss = {s["slug"]: s for s in P["us_statuses"]}; tss = {s["slug"]: s for s in P["task_statuses"]}; iss = {s["slug"]: s for s in P["issue_statuses"]}
pts = {p["value"]: p["id"] for p in P["points"]}; role = [r for r in P["roles"] if r["computable"]][0]
def g(path): return owner.get(path).json()
def mk_ms(n): return owner.post("/milestones", {"project": pid, "name": n, "estimated_start": "2026-11-01", "estimated_finish": "2026-11-30"}).json()

print("== user story status 'in-progress' (open) deleted with moveTo='done' (closed)")
m1 = mk_ms("m1")
us = owner.post("/userstories", {"project": pid, "subject": "a", "status": uss["in-progress"]["id"], "milestone": m1["id"], "points": {str(role["id"]): pts[5.0]}}).json()
print("delete ->", owner.delete(f"/userstory-statuses/{uss['in-progress']['id']}?moveTo={uss['done']['id']}").status_code)
u = g(f"/userstories/{us['id']}")
print(f"US status is 'done': {u['status']==uss['done']['id']}  is_closed={u['is_closed']}  finish_date={u['finish_date']}  milestone.closed={g('/milestones/%d' % m1['id'])['closed']}")
st = g(f"/milestones/{m1['id']}/stats"); print(f"sprint stats: completed_userstories={st['completed_userstories']} completed_points={st['completed_points']} last day open_points={st['days'][-1]['open_points']}")
ps = g(f"/projects/{pid}/stats"); print(f"project stats: closed_points={ps['closed_points']} of defined_points={ps['defined_points']}")

print("== task status 'in-progress' (open) deleted with moveTo='closed'")
us2 = owner.post("/userstories", {"project": pid, "subject": "b"}).json()
t = owner.post("/tasks", {"project": pid, "subject": "t", "user_story": us2["id"], "status": tss["in-progress"]["id"]}).json()
print("delete ->", owner.delete(f"/task-statuses/{tss['in-progress']['id']}?moveTo={tss['closed']['id']}").status_code)
tt = g(f"/tasks/{t['id']}"); print(f"task is_closed={tt['is_closed']} finished_date={tt['finished_date']}  its US is_closed={g('/userstories/%d' % us2['id'])['is_closed']} (only task is closed)")

print("== task status 'closed' deleted with moveTo='new' (open)")
us3 = owner.post("/userstories", {"project": pid, "subject": "c"}).json()
t3 = owner.post("/tasks", {"project": pid, "subject": "t3", "user_story": us3["id"], "status": tss["closed"]["id"]}).json()
print("delete ->", owner.delete(f"/task-statuses/{tss['closed']['id']}?moveTo={tss['new']['id']}").status_code)
tt = g(f"/tasks/{t3['id']}"); print(f"task is_closed={tt['is_closed']} finished_date={tt['finished_date']}  its US is_closed={g('/userstories/%d' % us3['id'])['is_closed']} (its only task is open)")

print("== issue status 'in-progress' deleted with moveTo='closed'")
m2 = mk_ms("m2")
i = owner.post("/issues", {"project": pid, "subject": "i", "status": iss["in-progress"]["id"], "milestone": m2["id"]}).json()
print("delete ->", owner.delete(f"/issue-statuses/{iss['in-progress']['id']}?moveTo={iss['closed']['id']}").status_code)
ii = g(f"/issues/{i['id']}"); print(f"issue is_closed={ii['is_closed']} finished_date={ii['finished_date']}  milestone.closed={g('/milestones/%d' % m2['id'])['closed']} (its only item is closed)")
print("control: a single PATCH of an issue to a closed status ->", end=" ")
i2 = owner.post("/issues", {"project": pid, "subject": "i2", "milestone": mk_ms("m3")["id"]}).json()
i2 = owner.patch(f"/issues/{i2['id']}", {"status": iss["closed"]["id"], "version": i2["version"]}).json()
print(f"finished_date set={i2['finished_date'] is not None} milestone.closed={g('/milestones/%d' % i2['milestone'])['closed']}")
