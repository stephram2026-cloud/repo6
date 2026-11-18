"""Bulk milestone move of user stories does not recalculate the milestone's closed flag.
A closed milestone stays closed=True after an OPEN story is moved into it."""
from lib import *
owner = register('own')
P = mkproject(owner)
closed = [s for s in P["us_statuses"] if s["is_closed"]][0]
openst = [s for s in P["us_statuses"] if not s["is_closed"]][0]
m = owner.post("/milestones", {"project": P["id"], "name": "s",
               "estimated_start": "2026-01-01", "estimated_finish": "2026-02-01"}).json()
owner.post("/userstories", {"project": P["id"], "subject": "closed-us", "status": closed["id"], "milestone": m["id"]})
print("milestone closed after a closed US added:", owner.get(f"/milestones/{m['id']}").json()["closed"])
uso = owner.post("/userstories", {"project": P["id"], "subject": "open-us", "status": openst["id"]}).json()
r = owner.post("/userstories/bulk_update_milestone", {"project_id": P["id"], "milestone_id": m["id"],
               "bulk_stories": [{"us_id": uso["id"], "order": 1}]})
print("bulk_update_milestone ->", r.status_code)
print("milestone closed after moving an OPEN us in:", owner.get(f"/milestones/{m['id']}").json()["closed"], "(should be False)")
print("stories:", [(u["subject"], u["is_closed"]) for u in owner.get(f"/userstories?milestone={m['id']}").json()])
