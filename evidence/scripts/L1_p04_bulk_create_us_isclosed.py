"""US bulk_create disconnects ALL userstory signals, so a US created in bulk with a
CLOSED status keeps is_closed=False (single create sets it True)."""
from lib import *
owner = register('own')
P = mkproject(owner)
closed = [s for s in P["us_statuses"] if s["is_closed"]][0]
single = owner.post("/userstories", {"project": P["id"], "subject": "single", "status": closed["id"]}).json()
print("single create (closed status) is_closed:", single["is_closed"], "finish_date:", single["finish_date"])
data = owner.post("/userstories/bulk_create",
                  {"project_id": P["id"], "status_id": closed["id"], "bulk_stories": "a\nb"}).json()
for u in data:
    uu = owner.get(f"/userstories/{u['id']}").json()
    print("bulk US ref", uu["ref"], "status", uu["status"], "is_closed", uu["is_closed"], "finish_date", uu["finish_date"])
