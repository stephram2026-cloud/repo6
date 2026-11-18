"""R2A-15: list filters that turn a malformed query value into HTTP 500 instead of 400."""
from lib import *
owner = register('r2o'); P = mkproject(owner); pid = P["id"]
owner.post("/userstories", {"project": pid, "subject": "s"})
for q in ["userstories?project=%d&created_date__gte=2026-01-01" % pid,
          "userstories?project=%d&created_date__gte=2026-02-30" % pid,
          "tasks?project=%d&finished_date__lt=yesterday" % pid,
          "issues?project=%d&created_date=31-31-2026" % pid,
          "milestones?project=%d&estimated_start__gte=2026-02-30" % pid,
          "userstories?project=%d&is_closed=true" % pid,
          "userstories?project=%d&is_closed=TRUE" % pid,
          "userstories?project=%d&status__is_archived=yes" % pid,
          "tasks?project=%d&status__is_closed=yes" % pid,
          "milestones?project=%d&closed=no" % pid,
          "userstories?project=%d&milestone=abc" % pid,
          "userstories?project=%d&order_by=epic_order" % pid,
          "userstories?project=%d&epic=abc" % pid]:
    r = owner.get("/" + q); print(r.status_code, "GET /" + q, r.text[:60] if r.status_code >= 400 else "")
