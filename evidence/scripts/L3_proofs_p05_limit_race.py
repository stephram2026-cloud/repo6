import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
import concurrent.futures as cf
s=suffix(); O=f"o5{s}"
mkusers(O, *[f"m5{s}{i}" for i in range(8)])
# set owner's max_memberships_private_projects to a small number
shell(f"from taiga.users.models import User; u=User.objects.get(username='{O}'); u.max_memberships_private_projects=3; u.save()")
P=mkproject(O,name=f"L-{s}")  # owner membership counts as 1
role=P["roles"][0]["id"]
# Now owner has 1 membership, limit 3 -> can add 2 more max. Fire 8 concurrent single-create invitations.
def inv(i):
    r=api(O,"POST","/memberships",dict(project=P["id"],role=role,username=f"m5{s}{i}@ex.test"))
    return r.status_code
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    res=list(ex.map(inv, range(8)))
print("statuses:",res)
tot=shell(f"from taiga.projects.models import Membership as M; print(M.objects.filter(project_id={P['id']}).count())").strip()
print("total memberships in project (limit was 3):", tot)
