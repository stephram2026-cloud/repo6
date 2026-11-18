"""R2A-13: the role filter (?role=<id>) is skipped when no member holds that role, so it returns
every row instead of none; filters_data reports count 0 for the same role."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
m = register('r2m'); roles = {r["name"]: r for r in P["roles"]}
add_member(owner, P, m, roles["Front"]["id"])
owner.post("/userstories", {"project": pid, "subject": "us of m", "assigned_to": m.user["id"]}); owner.post("/userstories", {"project": pid, "subject": "us unassigned"})
owner.post("/tasks", {"project": pid, "subject": "task of m", "assigned_to": m.user["id"]}); owner.post("/tasks", {"project": pid, "subject": "task unassigned"})
owner.post("/issues", {"project": pid, "subject": "issue of m", "assigned_to": m.user["id"]}); owner.post("/issues", {"project": pid, "subject": "issue unassigned"})
def subj(path): return sorted(x["subject"] for x in owner.get(path).json())
for kind in ("userstories", "tasks", "issues"):
    fd = {r["name"]: r["count"] for r in owner.get(f"/{kind}/filters_data?project={pid}").json()["roles"]}
    print(f"{kind}: filters_data roles Front={fd['Front']} Design={fd['Design']}")
    print(f"   ?role=Front  (1 member)  ->", subj(f"/{kind}?project={pid}&role={roles['Front']['id']}"))
    print(f"   ?role=Design (0 members) ->", subj(f"/{kind}?project={pid}&role={roles['Design']['id']}"))
