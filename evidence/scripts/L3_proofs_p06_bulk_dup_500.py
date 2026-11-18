import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
s=suffix(); O=f"o6{s}"; T=f"t6{s}"
mkusers(O,T)
P=mkproject(O,name=f"B6a-{s}")
add_member(O,P,f"{T}@ex.test")   # now T shares a project with O -> is a contact
Q=mkproject(O,name=f"B6b-{s}")
role=Q["roles"][0]["id"]
r=api(O,"POST","/memberships/bulk_create",dict(project_id=Q["id"],bulk_memberships=[
    {"username": T, "role_id": role},
    {"username": f"{T}@ex.test", "role_id": role},
]))
print("bulk same existing user by username+email:",r.status_code, r.text[:300])
