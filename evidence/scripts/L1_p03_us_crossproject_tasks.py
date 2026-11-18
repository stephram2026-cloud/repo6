"""Moving a US to another project leaves its tasks behind (task.project != task.user_story.project),
and deleting the moved US cascade-deletes a task that lives in the old project."""
from lib import *
owner = register('own')
P = mkproject(owner); Q = mkproject(owner)
us = owner.post("/userstories", {"project": P["id"], "subject": "u"}).json()
t = owner.post("/tasks", {"project": P["id"], "subject": "t", "user_story": us["id"]}).json()
print("before: us.project", us["project"], "task.project", t["project"])
owner.patch(f"/userstories/{us['id']}", {"project": Q["id"], "status": us["status"], "version": us["version"]})
us2 = owner.get(f"/userstories/{us['id']}").json(); t2 = owner.get(f"/tasks/{t['id']}").json()
print("after:  us.project", us2["project"], "task.project", t2["project"], " MISMATCH" if us2["project"] != t2["project"] else "")
print("task in Q list?", any(x['id']==t['id'] for x in owner.get(f"/tasks?project={Q['id']}").json()),
      "| task in P list?", any(x['id']==t['id'] for x in owner.get(f"/tasks?project={P['id']}").json()))
print("delete US in Q ->", owner.delete(f"/userstories/{us['id']}").status_code)
print("task (lived in P) after US delete ->", owner.get(f"/tasks/{t['id']}").status_code, "(404 => cross-project cascade delete)")
