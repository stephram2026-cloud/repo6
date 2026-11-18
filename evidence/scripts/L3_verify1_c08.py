from common import *
s = suffix(); A = f"c8a{s}"
mkusers(A)
def run(endpoint, field, extra_key):
    P = mkproject(A, name=f"C8-{field}-{extra_key}-{suffix()}"); pid = P["id"]
    u1 = mkus(A, P, "story1"); u2 = mkus(A, P, "story2")
    a = [mktask(A, P, f"a{i}", user_story=u1["id"]) for i in (1, 2, 3)]
    bY = mktask(A, P, "bY", user_story=u2["id"]); bX = mktask(A, P, "bX", user_story=u2["id"])
    ids = {t["id"]: t["subject"] for t in a + [bY, bX]}
    init = {a[0]["id"]: 1, a[1]["id"]: 2, a[2]["id"]: 3, bX["id"]: 2, bY["id"]: 3}
    shell("from taiga.projects.tasks.models import Task\n" + "\n".join(f"Task.objects.filter(id={i}).update({field}={o})" for i, o in init.items()))
    def view(us):
        r = api(A, "GET", f"/tasks?project={pid}&user_story={us['id']}&order_by={field}")
        return [(t["subject"], t["ref"], t[field]) for t in sorted(r.json(), key=lambda t: (t[field], t["ref"]))]
    def server(us):
        r = api(A, "GET", f"/userstories?project={pid}&include_tasks=1")
        return [t["subject"] for u in r.json() if u["id"] == us["id"] for t in u["tasks"]]
    print(f"== {endpoint} (field {field}), story filter sent as '{extra_key}'")
    print("  server-side task order in story2 (GET /userstories?include_tasks=1) before:", server(u2))
    print("  before story1:", view(u1)); print("  before story2:", view(u2))
    body = {"project_id": pid, extra_key: u1["id"], "bulk_tasks": [{"task_id": a[2]["id"], "order": 1}]}
    r = api(A, "POST", f"/tasks/{endpoint}", body)
    print("  request: move a3 to position 1 inside story1 ->", r.status_code, {ids[int(k)]: v for k, v in r.json().items()} if r.status_code == 200 else r.text)
    print("  after  story1:", view(u1)); print("  after  story2:", view(u2), " <-- story2 was not part of the request")
    print("  server-side task order in story2 after:", server(u2))
run("bulk_update_us_order", "us_order", "us_id")
run("bulk_update_us_order", "us_order", "user_story_id")
run("bulk_update_taskboard_order", "taskboard_order", "us_id")
