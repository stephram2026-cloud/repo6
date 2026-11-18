import sys; sys.path.insert(0,"/root/johto-task4/L3/scratch")
from lib import *
s=suffix(); O=f"o2{s}"
mkusers(O)
A=mkproject(O,name=f"A-{s}"); B=mkproject(O,name=f"B-{s}")
sa=api(O,"GET",f"/issue-statuses?project={A['id']}").json()
sb=api(O,"GET",f"/issue-statuses?project={B['id']}").json()
it=api(O,"GET",f"/issue-types?project={A['id']}").json()[0]
pr=api(O,"GET",f"/priorities?project={A['id']}").json()[0]
sv=api(O,"GET",f"/severities?project={A['id']}").json()[0]
victim_status=sa[2]  # the one we'll delete
issue=api(O,"POST","/issues",dict(project=A['id'],subject="x",status=victim_status['id'],type=it['id'],priority=pr['id'],severity=sv['id'])).json()
dest_in_B=sb[3]
r=api(O,"DELETE",f"/issue-statuses/{victim_status['id']}?moveTo={dest_in_B['id']}")
print("cross-project delete status:",r.status_code)
# reload the issue: what's its status now?
i2=api(O,"GET",f"/issues/{issue['id']}").json()
print("issue in project A now has status id",i2['status'],"which belongs to project", 
      shell(f"from taiga.projects.models import IssueStatus as S; print(S.objects.get(id={i2['status']}).project_id)").strip(),
      "but the issue's project is", i2['project'])
print("dest status project id (B):", dest_in_B['id'], B['id'])
