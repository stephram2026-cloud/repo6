import sys
sys.path.insert(0, '/root/johto-task4/L2/scratch/proofs')
from lib import *

o = register(uniq("owner"))
p = new_project(o)
P = p["id"]

def tags(label=""):
    pr = o.get("/projects/%s" % P).json()
    print(label, "tags_colors =", pr["tags_colors"])
    return pr["tags_colors"]

print("### Tag case-duplication: create 'abc' then 'ABC'")
show("create abc", o.post("/projects/%s/create_tag" % P, {"tag": "abc", "color": "#ff0000"}))
tags("after abc:")
show("create ABC (validator checks raw 'ABC', stores lowercase 'abc')",
     o.post("/projects/%s/create_tag" % P, {"tag": "ABC", "color": "#00ff00"}))
tags("after ABC:")

print("\n### edit_tag case-merge: existing 'keep' + rename 'abc' -> 'KEEP'")
show("create keep", o.post("/projects/%s/create_tag" % P, {"tag": "keep", "color": "#0000ff"}))
# tag an issue with abc and keep to see data effect
iss = o.post("/issues", {"project": P, "subject": "tagged", "tags": [["abc", "#ff0000"], ["keep", "#0000ff"]]}).json()
print("issue tags:", iss.get("tags"))
show("edit_tag from=abc to=KEEP (collides with existing 'keep' after lowercasing)",
     o.post("/projects/%s/edit_tag" % P, {"from_tag": "abc", "to_tag": "KEEP"}))
tags("after edit:")
print("issue now:", o.get("/issues/%s" % iss["id"]).json().get("tags"))
