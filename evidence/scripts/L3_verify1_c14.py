from common import *
import threading
s = suffix(); A = f"c14a{s}"; L = f"c14l{s}"
mkusers(A, L)
P = mkproject(A, name=f"C14-{s}"); pid = P["id"]
role = mkrole(A, P, "sprinter", ["view_project", "view_milestones", "add_milestone"])
addm(A, P, L, role=role["id"])
print("caller role perms:", role["permissions"])
def rss():
    o = subprocess.run(["docker", "exec", "t4-L3-app", "sh", "-c", "grep -H VmRSS /proc/[0-9]*/status 2>/dev/null"], capture_output=True, text=True).stdout
    return max([int(l.split()[1]) for l in o.splitlines() if l.split()[1:2]] or [0]) // 1024
def run(start, finish, timeout=400):
    r = api(L, "POST", "/milestones", dict(project=pid, name=f"s {start}..{finish}", estimated_start=start, estimated_finish=finish))
    if r.status_code != 201:
        print(f"{start}..{finish}: create -> {r.status_code} {r.text[:200]}"); return
    mid = r.json()["id"]; peak = [rss()]; stop = []
    def mon():
        while not stop: peak.append(rss()); time.sleep(0.5)
    th = threading.Thread(target=mon); th.start(); t0 = time.time()
    try:
        r = api(L, "GET", f"/milestones/{mid}/stats", timeout=timeout)
        dt = time.time() - t0
        try: days = len(r.json()["days"])
        except Exception: days = None
        res = f"HTTP {r.status_code}, {dt:.1f}s, body {len(r.content)/1e6:.1f} MB, days={days}" + ("" if days else f", body={r.text[:100]!r}")
    except Exception as e:
        res = f"client error after {time.time()-t0:.1f}s: {type(e).__name__} {str(e)[:120]}"
    stop.append(1); th.join()
    print(f"sprint {mid} {start}..{finish}: create 201; stats -> {res}; largest worker RSS {peak[0]} MB -> {max(peak)} MB", flush=True)
    return mid
import sys
for a, b in [("2026-01-01", "2026-01-15"), ("2026-01-01", "2036-01-01"), ("1926-01-01", "2126-01-01"), ("1026-01-01", "3026-01-01"), ("0001-01-01", "9999-12-30"), ("0001-01-01", "9999-12-31")]:
    run(a, b)
print("-- is the API still answering?", api(L, "GET", f"/projects/{pid}", timeout=60).status_code)
