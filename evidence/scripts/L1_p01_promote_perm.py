"""Promote task->US: permission is checked on request-body project_id, not the
task's own project. get_object() only needs view_tasks, so a non-privileged
member (or outsider on a public project) can promote and thereby DELETE a task."""
from lib import *

owner = register('own')
outsider = register('out')

# public project: outsiders get its public_permissions (view only)
pub = mkproject(owner, private=False)
print("public_permissions:", pub["public_permissions"])
t = owner.post("/tasks", {"project": pub["id"], "subject": "t-one"}).json()
print("task", t["id"], "ref", t["ref"])

# outsider has no delete/modify rights on this task
print("outsider DELETE task directly ->", outsider.delete(f"/tasks/{t['id']}").status_code)

# outsider makes their own project so they hold view_tasks SOMEWHERE
mine = mkproject(outsider, private=True)

# promote the public project's task, passing outsider's own project_id
r = outsider.post(f"/tasks/{t['id']}/promote_to_user_story", {"project_id": mine["id"]})
print("promote with project_id=own ->", r.status_code, r.text[:200])
print("task still exists? GET ->", owner.get(f"/tasks/{t['id']}").status_code)

# Case: private project, viewer-only member
priv = mkproject(owner, private=True)
viewer = register('view')
role = owner.post("/roles", {"project": priv["id"], "name": "ViewOnly",
                             "permissions": ["view_project", "view_tasks", "view_us"]}).json()
add_member(owner, priv, viewer, role["id"])
t3 = owner.post("/tasks", {"project": priv["id"], "subject": "t-priv"}).json()
print("viewer DELETE task ->", viewer.delete(f"/tasks/{t3['id']}").status_code)
r = viewer.post(f"/tasks/{t3['id']}/promote_to_user_story", {"project_id": priv["id"]})
print("viewer promote ->", r.status_code, r.text[:160], "| task GET ->",
      owner.get(f"/tasks/{t3['id']}").status_code)
