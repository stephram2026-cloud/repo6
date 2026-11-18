"""R2A-05: Project.update_role_points() returns early when the project has no computable role left,
so the role points of the LAST role made non-computable are never removed: stories keep the estimate,
stats keep counting it, and the API refuses to edit it."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
pts = {p["value"]: p["id"] for p in P["points"]}
comp = [r for r in P["roles"] if r["computable"]]
us = owner.post("/userstories", {"project": pid, "subject": "s", "points": {str(r["id"]): pts[2.0] for r in comp}}).json()
print("4 computable roles x 2 points: total_points =", us["total_points"])
for r in comp[:-1]:
    owner.patch(f"/roles/{r['id']}", {"computable": False})
u = owner.get(f"/userstories/{us['id']}").json(); print("3 roles made non-computable: total_points =", u["total_points"], "points =", u["points"])
last = comp[-1]
print("last computable role -> non-computable:", owner.patch(f"/roles/{last['id']}", {"computable": False}).status_code)
print("computable roles now:", [r["name"] for r in owner.get(f"/roles?project={pid}").json() if r["computable"]])
u = owner.get(f"/userstories/{us['id']}").json(); print("US total_points =", u["total_points"], "points =", u["points"], " (expected None / {})")
st = owner.get(f"/projects/{pid}/stats").json(); print("project stats defined_points =", st["defined_points"], "defined_points_per_role =", st["defined_points_per_role"])
r = owner.patch(f"/userstories/{us['id']}", {"points": {str(last["id"]): pts[None]}, "version": u["version"]}); print("try to clear the estimate ->", r.status_code, r.text[:120])
