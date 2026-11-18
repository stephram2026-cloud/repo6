"""Sending the user-story 'points' field as anything that is not a dict and not valid
JSON (a plain string, or a number) crashes RolePointsField.from_native with an
uncaught JSONDecodeError/TypeError -> HTTP 500."""
from lib import *
owner = register('own'); P = mkproject(owner)
us = owner.post("/userstories", {"project": P["id"], "subject": "u"}).json()
for val in ["notjson", "[1,2", 123]:
    r = owner.patch(f"/userstories/{us['id']}", {"points": val, "version": us["version"]})
    print(repr(val), "->", r.status_code, r.text[:80])
