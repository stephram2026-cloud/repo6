# in-container helper: replay one API request through Django's test client so the exception behind a 500 is visible
# usage: python /scratch/verify1/inproc.py <username> <METHOD> <path> '<json body>'
import sys, os, json, traceback
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.config")
sys.path.insert(0, "/taiga-back")
import django; django.setup()
from django.test import Client
from taiga.users.models import User
from taiga.auth.tokens import AccessToken
u, method, path, body = sys.argv[1], sys.argv[2], sys.argv[3], (sys.argv[4] if len(sys.argv) > 4 else None)
c = Client(raise_request_exception=True)
h = {}
if u != "-":
    h["HTTP_AUTHORIZATION"] = "Bearer " + str(AccessToken.for_user(User.objects.get(username=u)))
try:
    r = getattr(c, method.lower())("/api/v1" + path, data=body, content_type="application/json", **h)
    print("HTTP", r.status_code, r.content[:300])
except BaseException as e:
    tb = traceback.format_exc().strip().splitlines()
    print("EXCEPTION:", type(e).__module__ + "." + type(e).__name__, str(e)[:300].replace("\n", " | "))
    print("\n".join(l for l in tb if "/taiga-back/taiga/" in l)[-900:])
