import sys; sys.path.insert(0, "/root/johto-task4/L3/scratch")
from lib import *

def mkrole(admin, project, name, perms):
    r = api(admin, "POST", "/roles", dict(project=project["id"], name=name, permissions=perms, computable=True))
    assert r.status_code == 201, r.text
    return r.json()
def mkus(u, project, subject="us", **kw):
    r = api(u, "POST", "/userstories", dict(project=project["id"], subject=subject, **kw)); assert r.status_code == 201, r.text; return r.json()
def mktask(u, project, subject="task", **kw):
    r = api(u, "POST", "/tasks", dict(project=project["id"], subject=subject, **kw)); assert r.status_code == 201, r.text; return r.json()
def mkissue(u, project, subject="issue", **kw):
    r = api(u, "POST", "/issues", dict(project=project["id"], subject=subject, **kw)); assert r.status_code == 201, r.text; return r.json()
def mkepic(u, project, subject="epic", **kw):
    r = api(u, "POST", "/epics", dict(project=project["id"], subject=subject, **kw)); assert r.status_code == 201, r.text; return r.json()
def mkms(u, project, name="sprint", start="2026-01-01", finish="2026-01-15", **kw):
    r = api(u, "POST", "/milestones", dict(project=project["id"], name=name, estimated_start=start, estimated_finish=finish, **kw)); assert r.status_code == 201, r.text; return r.json()
def getp(u, pid): return api(u, "GET", f"/projects/{pid}").json()
def addm(admin, project, user, role=None, is_admin=False):
    return add_member(admin, project, f"{user}@ex.test", role=role, is_admin=is_admin)
