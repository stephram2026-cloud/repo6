"""R2A-01: two concurrent PATCHes on different fields of one user story (same client version).
UserStoryViewSet.update loads self.object BEFORE UpdateModelMixin.update takes the
model_pk_lock advisory lock, so the second request saves its stale copy of every column
and silently reverts the first request's change. OCC lets it through because the
modified-field sets do not intersect."""
import threading, sys
from lib import *

kind = sys.argv[1] if len(sys.argv) > 1 else "userstories"
owner = register('r2o'); P = mkproject(owner)
if kind == "epics":
    owner.patch(f"/projects/{P['id']}", {"is_epics_activated": True})
c1, c2 = C(owner.user["username"]), C(owner.user["username"])
lost = 0; N = 20
for i in range(N):
    o = owner.post(f"/{kind}", {"project": P["id"], "subject": f"orig{i}", "description": "orig-desc"}).json()
    b = threading.Barrier(2); res = {}
    def go(c, key, body):
        b.wait(); res[key] = c.patch(f"/{kind}/{o['id']}", dict(body, version=o["version"]))
    t1 = threading.Thread(target=go, args=(c1, "subject", {"subject": f"NEW-SUBJECT-{i}"}))
    t2 = threading.Thread(target=go, args=(c2, "description", {"description": "NEW-DESC"}))
    t1.start(); t2.start(); t1.join(); t2.join()
    f = owner.get(f"/{kind}/{o['id']}").json()
    ok = f["subject"].startswith("NEW") and f["description"] == "NEW-DESC"
    if not ok and res["subject"].status_code == 200 and res["description"].status_code == 200:
        lost += 1
        if lost <= 3:
            h = owner.get(f"/history/{kind[:-1] if kind!='userstories' else 'userstory'}/{o['id']}").json()
            print(f"iter {i}: both PATCH 200; final subject={f['subject']!r} description={f['description']!r} version={f['version']}")
            print("   history diffs:", [list(e['diff'].keys()) for e in h])
print(f"{kind}: {lost}/{N} rounds lost one of two successful, non-conflicting updates")
