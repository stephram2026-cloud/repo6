"""R2A-08: votes.services.remove_vote checks "has this user voted?" inside the advisory lock but
deletes the Vote row and decrements Votes.count AFTER releasing it. Two downvote requests by the
same user (double click / two tabs) both pass the check and both decrement.
Usage: python3 r2a08_downvote_race.py [rounds]"""
import threading, sys
from lib import *
owner = register('r2o'); P = mkproject(owner, private=False); pid = P["id"]
other = register('r2v')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
K = int(sys.argv[2]) if len(sys.argv) > 2 else 4
clients = [C(owner.user["username"]) for _ in range(K)]
bad = err = 0
for it in range(N):
    us = owner.post("/userstories", {"project": pid, "subject": f"u{it}"}).json()
    assert owner.post(f"/userstories/{us['id']}/upvote").status_code == 200
    assert other.post(f"/userstories/{us['id']}/upvote").status_code == 200
    b = threading.Barrier(K); codes = []
    def go(c):
        b.wait(); codes.append(c.post(f"/userstories/{us['id']}/downvote").status_code)
    ths = [threading.Thread(target=go, args=(c,)) for c in clients]
    [t.start() for t in ths]; [t.join() for t in ths]
    u = owner.get(f"/userstories/{us['id']}").json()
    voters = [v["username"] for v in owner.get(f"/userstories/{us['id']}/voters").json()]
    if any(c >= 500 for c in codes): err += 1
    if u["total_voters"] != len(voters):
        bad += 1
        if bad <= 3: print(f"round {it}: downvote responses {sorted(codes)}; voters list has {len(voters)} user(s) but total_voters={u['total_voters']}")
print(f"{bad}/{N} rounds ended with total_voters != number of voters; {err} rounds had a 5xx")
