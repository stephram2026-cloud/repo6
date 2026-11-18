from common import *
s = suffix(); O = f"c7o{s}"; Y = f"c7y{s}"; XU = f"c7x{s}"; XE = f"invited-{s}@ex.test"
mkusers(O, Y)
P = mkproject(O, name=f"C7-{s}"); pid = P["id"]
roles = {r["name"]: r["id"] for r in P["roles"]}; print("roles:", roles)
r1, r2 = list(roles.values())[0], list(roles.values())[1]
def st(mid):
    return shell(f"from taiga.projects.models import Membership as M; m=M.objects.get(id={mid}); print('membership', m.id, 'project', m.project_id, 'email=', m.email, 'user=', (m.user_id, m.user.username, m.user.email) if m.user else None, 'role=', m.role_id, 'is_admin=', m.is_admin, 'token=', m.token)").strip()
print("1. owner invites address X =", XE, "(no account has it), as admin to make the effect clear")
r = api(O, "POST", "/memberships", dict(project=pid, role=r1, username=XE, is_admin=True)); print(r.status_code, r.text[:200]); m = r.json(); mid = m["id"]
print("  ", st(mid))
token = shell(f"from taiga.projects.models import Membership as M; print(M.objects.get(id={mid}).token)").strip()
print("2. existing account Y (email %s@ex.test) accepts with the invitation token at login" % Y)
r = requests.post(BASE + "/auth", json={"type": "normal", "username": Y, "password": "123123", "invitation_token": token}); print(r.status_code, r.json().get("email"))
print("  ", st(mid))
print("   Y sees project:", api(Y, "GET", f"/projects/{pid}").status_code)
print("3. somebody registers a NEW account with email X (public registration)")
r = requests.post(BASE + "/auth/register", json={"type": "public", "username": XU, "email": XE, "password": "123123qwe", "full_name": "X Person", "accepted_terms": True}); print(r.status_code, r.text[:160])
print("  ", st(mid))
xtok = r.json().get("auth_token")
hx = {"Authorization": "Bearer " + xtok} if xtok else {}
print("   X sees project before role change:", requests.get(BASE + f"/projects/{pid}", headers=hx).status_code)
print("4. owner changes the role of that membership: PATCH /memberships/%d {role: %d}" % (mid, r2))
r = api(O, "PATCH", f"/memberships/{mid}", {"role": r2}); print(r.status_code, {k: r.json().get(k) for k in ("id", "user", "email", "role", "is_admin", "full_name")} if r.status_code == 200 else r.text[:300])
print("  ", st(mid))
print("   Y sees project now:", api(Y, "GET", f"/projects/{pid}").status_code)
r = requests.get(BASE + f"/projects/{pid}", headers=hx); print("   X sees project now:", r.status_code, "i_am_admin=", r.json().get("i_am_admin"), "i_am_member=", r.json().get("i_am_member"))
print("   members of project:", shell(f"from taiga.projects.models import Membership as M; print([(m.id, m.user and m.user.username, m.email) for m in M.objects.filter(project_id={pid})])").strip())
