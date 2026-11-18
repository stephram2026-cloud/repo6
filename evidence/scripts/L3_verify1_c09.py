from common import *
s = suffix(); U = f"c9u{s}"; V = f"c9v{s}"
mkusers(U, V)
def counts(u):
    return shell(f"from taiga.users.models import User; u=User.objects.get(username='{u}'); print('max_private=',u.max_private_projects,'max_public=',u.max_public_projects,'owned private=',u.owned_projects.filter(is_private=True).count(),'owned public=',u.owned_projects.filter(is_private=False).count())").strip()
print("=== Case 1: wrongly ALLOWED (private limit bypass)")
shell(f"from taiga.users.models import User; User.objects.filter(username='{U}').update(max_private_projects=1, max_public_projects=5)")
priv = mkproject(U, name=f"C9-priv-{s}", is_private=True)
pub = mkproject(U, name=f"C9-pub-{s}", is_private=False)
shell(f"from taiga.projects.models import Project; Project.objects.filter(id={pub['id']}).update(owner_id={uid(V)})") if False else None
print(counts(U))
print("control: create a 2nd private project directly:", end=" "); show(api(U, "POST", "/projects", dict(name="second private", description="d", is_private=True, creation_template=1)), 200)
print("control: duplicate the PRIVATE project as private:", end=" "); show(api(U, "POST", f"/projects/{priv['id']}/duplicate", dict(name="dup-priv", description="d", is_private=True, users=[])), 200)
print("claim  : duplicate the PUBLIC project as private:", end=" "); r = api(U, "POST", f"/projects/{pub['id']}/duplicate", dict(name=f"dup-from-pub-{s}", description="d", is_private=True, users=[])); print(r.status_code, {k: r.json().get(k) for k in ("id","name","is_private","owner")} if r.status_code == 201 else r.text[:200])
print(counts(U))
print("=== Case 2: wrongly REFUSED")
shell(f"from taiga.users.models import User; User.objects.filter(username='{V}').update(max_private_projects=5, max_public_projects=1)")
vpriv = mkproject(V, name=f"C9v-priv-{s}", is_private=True)
print(counts(V))
print("claim  : duplicate the PRIVATE project as public (V owns 0 public, limit 1):", end=" "); show(api(V, "POST", f"/projects/{vpriv['id']}/duplicate", dict(name=f"dupv-{s}", description="d", is_private=False, users=[])), 300)
print("control: create a public project directly:", end=" "); r = api(V, "POST", "/projects", dict(name=f"C9v-pub-{s}", description="d", is_private=False, creation_template=1)); print(r.status_code, r.json().get("is_private"))
print(counts(V))
