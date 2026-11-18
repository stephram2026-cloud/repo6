"""tasks bulk_update_milestone / milestones move_tasks_to_sprint let a task that belongs
to a user story be moved to a different sprint than its US. The validator only checks the
task's project and the milestone's project, not that the task has no US or that its US is in
the same milestone. Everywhere else task.milestone is forced to equal us.milestone."""
from lib import *
owner = register('own'); P = mkproject(owner)
def ms(n): return owner.post("/milestones", {"project": P["id"], "name": n, "estimated_start":"2026-01-01","estimated_finish":"2026-02-01"}).json()
m1, m2 = ms("s1"), ms("s2")
us = owner.post("/userstories", {"project": P["id"], "subject": "u", "milestone": m1["id"]}).json()
t = owner.post("/tasks", {"project": P["id"], "subject": "t", "user_story": us["id"]}).json()
print("before: task.milestone", t["milestone"], "us.milestone", us["milestone"])
r = owner.post("/tasks/bulk_update_milestone", {"project_id": P["id"], "milestone_id": m2["id"],
               "bulk_tasks": [{"task_id": t["id"], "order": 1}]})
print("bulk_update_milestone ->", r.status_code)
t2 = owner.get(f"/tasks/{t['id']}").json(); us2 = owner.get(f"/userstories/{us['id']}").json()
print("after:  task.milestone", t2["milestone"], "task.user_story", t2["user_story"], "us.milestone", us2["milestone"],
      "=> DESYNC" if t2["milestone"] != us2["milestone"] else "")
print("m2 (sprint w/o the US) total_tasks in stats:", owner.get(f"/milestones/{m2['id']}/stats").json()["total_tasks"])
