"""R2A-07: add_like/remove_like recompute Project.total_fans with COUNT(*) inside each request's own
transaction and write it back (read-modify-write, no lock). Two users liking the same project at the
same moment each count only their own like."""
import threading
from lib import *
owner = register('r2o')
fans = [register('r2f') for _ in range(4)]
bad = 0; N = 15
for it in range(N):
    P = mkproject(owner, private=False)
    b = threading.Barrier(len(fans)); codes = []
    def go(c):
        b.wait(); codes.append(c.post(f"/projects/{P['id']}/like").status_code)
    ths = [threading.Thread(target=go, args=(c,)) for c in fans]
    [t.start() for t in ths]; [t.join() for t in ths]
    p = owner.get(f"/projects/{P['id']}").json()
    real = len(owner.get(f"/projects/{P['id']}/fans").json())
    if p["total_fans"] != real:
        bad += 1
        if bad <= 3: print(f"round {it}: like responses {codes}; fans list has {real} users but project.total_fans={p['total_fans']}")
print(f"{bad}/{N} rounds ended with total_fans != number of fans")
