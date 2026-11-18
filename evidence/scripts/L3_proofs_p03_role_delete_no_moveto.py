import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
s=suffix(); O=f"o3{s}"
mkusers(O)
P=mkproject(O,name=f"R-{s}")
roles=api(O,"GET",f"/roles?project={P['id']}").json()
print("roles:",[(r['id'],r['slug'],r.get('members')) for r in roles])
# find the owner's role
owner_role_id=shell(f"from taiga.projects.models import Membership as M; m=M.objects.get(project_id={P['id']},user__username='{O}'); print(m.role_id, m.is_admin)").strip()
print("owner membership role_id,is_admin:",owner_role_id)
rid=int(owner_role_id.split()[0])
# delete that role WITHOUT moveTo
r=api(O,"DELETE",f"/roles/{rid}")
print("delete owner's role no moveTo:",r.status_code,r.text[:150])
left=shell(f"from taiga.projects.models import Membership as M,Project as P; p=P.objects.get(id={P['id']}); print('memberships', [(m.user_id,m.is_admin) for m in p.memberships.all()], 'owner', p.owner_id, 'valid_admins', p.memberships.filter(is_admin=True,user__is_active=True).count())").strip()
print(left)
