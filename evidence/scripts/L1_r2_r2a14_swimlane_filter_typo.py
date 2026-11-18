"""R2A-14: SwimlanesFilter.param_name is misspelled "swimnlane": ?swimlane=<id> is silently ignored
while ?exclude_swimlane=<id> works."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
a = owner.post("/swimlanes", {"project": pid, "name": "A"}).json(); b = owner.post("/swimlanes", {"project": pid, "name": "B"}).json()
owner.post("/userstories", {"project": pid, "subject": "in A", "swimlane": a["id"]}); owner.post("/userstories", {"project": pid, "subject": "in B", "swimlane": b["id"]})
def subj(q): return sorted(x["subject"] for x in owner.get(f"/userstories?project={pid}&{q}").json())
print("?swimlane=A          ->", subj(f"swimlane={a['id']}"))
print("?exclude_swimlane=A  ->", subj(f"exclude_swimlane={a['id']}"))
print("?swimnlane=A (typo)  ->", subj(f"swimnlane={a['id']}"))
