import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
s=suffix(); O=f"o7{s}"; M=f"m7{s}"
mkusers(O,M)
P=mkproject(O,name=f"W7-{s}",is_private=True)
mem=add_member(O,P,f"{M}@ex.test")
# M watches the project (as a member would, or auto notify policy created on join)
print("member joined; notify policy exists:",
      shell(f"from taiga.projects.notifications.models import NotifyPolicy as NP; from taiga.users.models import User; u=User.objects.get(username='{M}'); print(NP.objects.filter(project_id={P['id']},user=u).exists())").strip())
# M explicitly watches to have notify_level != none
api(M,"POST",f"/projects/{P['id']}/watch",{"notify_level":1})
# Owner removes M from the project
r=api(O,"DELETE",f"/memberships/{mem['id']}")
print("remove member:",r.status_code)
out=shell(f"""
from taiga.projects.models import Project
from taiga.projects.notifications.models import NotifyPolicy as NP
from taiga.users.models import User
u=User.objects.get(username='{M}'); p=Project.objects.get(id={P['id']})
print('still a member:', p.memberships.filter(user=u).exists())
print('notify policy still exists:', NP.objects.filter(project=p,user=u).exists())
print('is in project watchers (gets notifications):', p.get_watchers().filter(id=u.id).exists())
""")
print(out)
