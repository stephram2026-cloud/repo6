import sys; sys.path.insert(0, "/root/johto-task4/L2/scratch/proofs")
from lib import Client, register, uniq, new_project, show

owner = register(uniq("r2own"))
outsider = register(uniq("r2out"))   # member of NO project
P = new_project(owner, private=True)
pid = P["id"]
print("project", pid, "owner", owner.user["id"], "outsider", outsider.user["id"])

# create a user story in P
r = owner.post("/userstories", {"project": pid, "subject": "us1"})
show("create US", r, keys=["id","subject"])
us = r.json(); usid = us["id"]

# 1) assigned_to to a NON member -> should be rejected (validator exists)
r = owner.patch("/userstories/%d" % usid, {"assigned_to": outsider.user["id"], "version": us["version"]})
show("PATCH assigned_to=outsider (non-member)", r, keys=["assigned_to","_error_message"])

# refetch version
us = owner.get("/userstories/%d" % usid).json()
# 2) assigned_users to a NON member -> is it rejected?
r = owner.patch("/userstories/%d" % usid, {"assigned_users": [outsider.user["id"]], "version": us["version"]})
show("PATCH assigned_users=[outsider] (non-member)", r, keys=["assigned_users","assigned_to","_error_message"])

# verify persisted in DB
import subprocess
code = ("from taiga.projects.userstories.models import UserStory\n"
        "us=UserStory.objects.get(pk=%d)\n"
        "print('assigned_users_ids', list(us.assigned_users.values_list('id',flat=True)))\n"
        "from taiga.projects.models import Membership\n"
        "print('outsider is member?', Membership.objects.filter(project_id=%d, user_id=%d).exists())\n" % (usid, pid, outsider.user["id"]))
out = subprocess.run(["docker","exec","t4-L2-app","python","manage.py","shell","-c",code], capture_output=True, text=True)
print(out.stdout.strip()); print(out.stderr.strip()[-300:] if out.returncode else "")

# 3) does the outsider now see it in their "assigned to me" via filter? (private project -> should NOT leak)
r = outsider.get("/userstories", params={"assigned_users": str(outsider.user["id"])})
show("outsider lists /userstories?assigned_users=self", r)
