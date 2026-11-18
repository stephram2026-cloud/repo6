"""R2A-06: the delete signals of US / task / issue can only CLOSE a milestone, never reopen it.
Deleting the last item of a closed sprint leaves an empty sprint with closed=True, while moving the
same item out of the sprint reopens it."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
uss = {s["slug"]: s for s in P["us_statuses"]}; iss = {s["slug"]: s for s in P["issue_statuses"]}
def g(path): return owner.get(path).json()
def mk_ms(n): return owner.post("/milestones", {"project": pid, "name": n, "estimated_start": "2026-11-01", "estimated_finish": "2026-11-30"}).json()
a = mk_ms("sprint A"); b = mk_ms("sprint B"); c = mk_ms("sprint C")
ua = owner.post("/userstories", {"project": pid, "subject": "a", "milestone": a["id"], "status": uss["done"]["id"]}).json()
ub = owner.post("/userstories", {"project": pid, "subject": "b", "milestone": b["id"], "status": uss["done"]["id"]}).json()
ic = owner.post("/issues", {"project": pid, "subject": "c", "milestone": c["id"], "status": iss["closed"]["id"]}).json()
print("closed flags with one closed item each:", [g(f"/milestones/{m['id']}")["closed"] for m in (a, b, c)])
print("A: DELETE the story ->", owner.delete(f"/userstories/{ua['id']}").status_code)
print("B: PATCH the story to the backlog ->", owner.patch(f"/userstories/{ub['id']}", {"milestone": None, "version": ub["version"]}).status_code)
print("C: DELETE the issue ->", owner.delete(f"/issues/{ic['id']}").status_code)
for m in (a, b, c):
    x = g(f"/milestones/{m['id']}"); print(f"{x['name']}: user_stories={len(x['user_stories'])} closed={x['closed']}")
r = owner.get(f"/milestones?project={pid}&closed=false"); print("open sprints listed (closed=false):", [x["name"] for x in r.json()], "| header opened/closed:", r.headers.get("Taiga-Info-Total-Opened-Milestones"), "/", r.headers.get("Taiga-Info-Total-Closed-Milestones"))
