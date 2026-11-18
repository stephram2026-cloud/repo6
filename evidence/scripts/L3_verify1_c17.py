from common import *
s = suffix(); A = f"c17a{s}"; M = f"c17m{s}"; MO = f"c17o{s}"
mkusers(A, M, MO)
P = mkproject(A, name=f"C17-{s}"); pid = P["id"]; rn = P["roles"][0]["id"]
addm(A, P, M, role=rn); addm(A, P, MO, role=rn)
usn = mkus(A, P, "assignable")
m_id, mo_id, a_id = uid(M), uid(MO), uid(A)
# ensure notify policies exist with web_notify_level True (default on membership creation)
print("notify policies:", shell(f"from taiga.projects.notifications.models import NotifyPolicy as N; print([(p.user.username, p.web_notify_level) for p in N.objects.filter(project_id={pid})])").strip())
def wn(uid_):
    return int(shell(f"from taiga.projects.notifications.models import WebNotification as W; print(W.objects.filter(user_id={uid_}).count())").strip() or 0)
ver = api(A, "GET", f"/userstories/{usn['id']}").json()["version"]
def setau(users, note):
    global ver
    bM, bMO = wn(m_id), wn(mo_id)
    r = api(A, "PATCH", f"/userstories/{usn['id']}", {"assigned_users": users, "version": ver})
    if r.status_code == 200: ver = r.json()["version"]
    time.sleep(0.5)
    print(f"  {note}: set={users} HTTP {r.status_code}; new WebNotifications -> M(already-set? )={wn(m_id)-bM}, MO={wn(mo_id)-bMO}")
setau([m_id], "(1) assign M for the first time")
setau([m_id, mo_id], "(2) add MO while M stays assigned")
setau([m_id, mo_id], "(3) PATCH same set again (no real change)")
setau([a_id, m_id, mo_id], "(4) add the editor A too (M, MO stay)")
print("Explanation check: result.data['assigned_users'] items are ints; old list holds User objects ->")
print(shell("from taiga.users.models import User; u=User.objects.first(); print('int in [User]:', (u.id in [u]), '| int==User:', (u.id==u))").strip())
