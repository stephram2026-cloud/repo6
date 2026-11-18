import sys; sys.path.insert(0, "/root/johto-task4/L2/scratch/proofs")
from lib import Client, register, uniq, new_project, show

owner = register(uniq("r2own6"))
anon = Client()
P = new_project(owner, private=False)  # public
pid = P["id"]
# restrict: grant view_project but NOT view_us to anon/public
owner.patch("/projects/%d" % pid, {"anon_permissions": ["view_project"], "public_permissions": ["view_project"]})
chk = owner.get("/projects/%d" % pid).json()
print("anon_permissions now:", chk.get("anon_permissions"))

# create a US with sensitive subject/description, then edit to make history + add a comment
us = owner.post("/userstories", {"project": pid, "subject":"SENSITIVE secret feature", "description":"confidential details"}).json()
usid = us["id"]
owner.patch("/userstories/%d" % usid, {"subject":"SENSITIVE secret feature v2","version":us["version"]})
us2 = owner.get("/userstories/%d" % usid).json()
owner.patch("/userstories/%d" % usid, {"comment":"internal comment leak-me","version":us2["version"]})

# anon cannot read the US object itself
show("ANON GET /userstories/%d" % usid, anon.get("/userstories/%d" % usid), keys=["id","subject","_error_message"])
# but can read its full history?
r = anon.get("/history/userstory/%d" % usid)
try:
    body = r.json()
    print("ANON GET /history/userstory -> HTTP", r.status_code, "entries:", len(body) if isinstance(body,list) else body)
    if isinstance(body, list):
        for e in body[:4]:
            print("  diff keys:", list((e.get("diff") or {}).keys()), "| comment:", repr(e.get("comment")), "| values:", e.get("values_diff") if False else "")
        import json as _j
        print("  RAW first entry snippet:", _j.dumps(body[0])[:500])
except Exception as ex:
    print("ANON history -> HTTP", r.status_code, r.text[:300])
