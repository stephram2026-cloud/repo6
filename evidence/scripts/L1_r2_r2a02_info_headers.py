"""R2A-02: list endpoints add Taiga-Info-* headers computed from the raw project id in the query
string, with no permission check -> counts of a private project leak to anonymous callers."""
from lib import *
owner = register('r2o'); P = mkproject(owner, private=True)
ms = owner.post("/milestones", {"project": P["id"], "name": "s1", "estimated_start": "2026-11-01", "estimated_finish": "2026-11-15"}).json()
owner.post("/milestones", {"project": P["id"], "name": "s2", "estimated_start": "2026-11-16", "estimated_finish": "2026-11-30"})
for i in range(3):
    owner.post("/userstories", {"project": P["id"], "subject": f"secret {i}"})
anon = C()
outsider = register('r2x')
for who, c in (("anonymous", anon), ("outsider", outsider)):
    r = c.get(f"/projects/{P['id']}"); print(who, "GET project ->", r.status_code)
    r = c.get(f"/userstories?project={P['id']}&milestone=null")
    print(who, "GET /userstories ->", r.status_code, "rows:", len(r.json()), {k: v for k, v in r.headers.items() if k.lower().startswith("taiga-info")})
    r = c.get(f"/milestones?project={P['id']}")
    print(who, "GET /milestones ->", r.status_code, "rows:", len(r.json()), {k: v for k, v in r.headers.items() if k.lower().startswith("taiga-info")})
# robustness of the same helper
r = owner.get("/milestones?project=abc"); print("milestones?project=abc ->", r.status_code)
r = owner.get("/userstories?project=abc"); print("userstories?project=abc ->", r.status_code)
r = owner.get(f"/milestones?project={P['id']},1"); print("milestones?project=<id>,1 ->", r.status_code)
r = owner.get(f"/userstories?project={P['id']},1"); print("userstories?project=<id>,1 ->", r.status_code)
