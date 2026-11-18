# run inside the container: python /scratch/verify1/listen.py <seconds> <channel> [<channel> ...]
import sys, select, time, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.config")
sys.path.insert(0, "/taiga-back")
import django; django.setup()
from django.db import connection
connection.ensure_connection()
c = connection.connection; c.autocommit = True
cur = c.cursor()
for ch in sys.argv[2:]:
    cur.execute('LISTEN "%s"' % ch)
print("LISTENING", sys.argv[2:], flush=True)
end = time.time() + float(sys.argv[1])
while time.time() < end:
    if select.select([c], [], [], 0.5)[0]:
        c.poll()
        while c.notifies:
            n = c.notifies.pop(0)
            print("NOTIFY channel=%s payload=%s" % (n.channel, n.payload), flush=True)
print("DONE", flush=True)
