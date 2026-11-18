import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
s=suffix(); O=f"o8{s}"; V=f"v8{s}"
mkusers(O,V)
A=mkproject(O,name=f"A8-{s}")
B=mkproject(V,name=f"B8-{s}")   # different owner; O is NOT a member/admin of B
# create a uniquely-named role in A
cr=api(O,"POST","/roles",dict(project=A['id'],name=f"Uniq{s}",permissions=["view_project"]))
rid=cr.json()['id']; print("created role in A:",rid, cr.status_code)
# assign a member of A to that role so we can see corruption
mem=add_member(O,A,f"{V}@ex.test")   # hmm V owns B; make a 3rd user instead
# move the role to project B (O has no rights on B)
r=api(O,"PATCH",f"/roles/{rid}",{"project":B['id'],"name":f"Uniq{s}"})
print("move role A->B:",r.status_code,r.text[:150])
print(shell(f"from taiga.users.models import Role; rr=Role.objects.get(id={rid}); print('role now project',rr.project_id,'A=',{A['id']},'B=',{B['id']})").strip())
