"""Task bulk_create disconnects set_finished_date_when_edit_task, so a task created in
bulk with a CLOSED status has finished_date=None (single create sets it). Burndown
(total_closed_points_by_date) excludes tasks with finished_date IS NULL."""
from lib import *
owner = register('own')
P = mkproject(owner)
tclosed = [s for s in P["task_statuses"] if s["is_closed"]][0]
m = owner.post("/milestones", {"project": P["id"], "name": "s",
               "estimated_start": "2026-01-01", "estimated_finish": "2026-02-01"}).json()
us = owner.post("/userstories", {"project": P["id"], "subject": "u", "milestone": m["id"]}).json()
tb = owner.post("/tasks/bulk_create", {"project_id": P["id"], "us_id": us["id"], "milestone_id": m["id"],
                "status_id": tclosed["id"], "bulk_tasks": "bulktask"}).json()[0]
ts = owner.post("/tasks", {"project": P["id"], "subject": "singletask", "user_story": us["id"],
                "status": tclosed["id"], "milestone": m["id"]}).json()
print("bulk-created closed task finished_date:", tb["finished_date"])
print("single-created closed task finished_date:", ts["finished_date"])
