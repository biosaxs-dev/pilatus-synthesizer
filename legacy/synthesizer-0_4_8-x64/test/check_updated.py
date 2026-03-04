"""
    check_updated.py

    Copyright (c) 2021-2023, SAXS Team, KEK-PF
"""
import sys
import os
import getopt
from shutil import copy2
from time import localtime, strftime

lib_dir = '..'

exclude_list = ["check_updated.py", "Version.py", "TesterDialog.py"]

optlist, args = getopt.getopt(sys.argv[1:], 'n:s:v:T:f:')
optdict = dict(optlist)

def pastdate(n=0):
    from datetime import datetime, timedelta
    pasttime = datetime.today() - timedelta(days=n)
    return pasttime.strftime("%Y-%m-%d")

n = int(optdict.get('-n', '0'))
s = optdict.get('-s', 'P')
v = optdict.get('-v', '2')
T = optdict.get('-T')
f = optdict.get('-f')
if T is not None:
    check_path = os.path.join(T, "molass.exe")
    assert os.path.exists(check_path)

v1_only = v == "1"

V2_Folders = ["Optimizer", "Rgg", "RgProcess", "SecTheory"]

def is_v2_folder(path):
    found = False
    for f in V2_Folders:
        if path.find(f) >= 0:
            found = True
    return found

if f is None:
    from_date = pastdate(n)
else:
    from_date = f
print("from_date=", from_date)

latest_time = None
latest_path = None
found_files = []
for root, dirs, files in os.walk(lib_dir):
    # print("root=", root)
    if root.find("embeddables") >= 0:
        continue

    if v1_only and is_v2_folder(root):
        continue

    found = False
    for f in files:
        if f[-3:] == ".py":
            if f in exclude_list:
                continue
            if v1_only and f.find("test_7") >= 0:
                continue

            path = os.path.join(root, f)
            modified_time = strftime("%Y-%m-%d %H:%M:%S", localtime(os.path.getmtime(path)))
            if latest_time is None or modified_time > latest_time:
                latest_time = modified_time
                latest_path = path
            if modified_time >= from_date:
                found_files.append((path, modified_time))


if s.lower().find("t") >= 0:
    found_files = sorted(found_files, key=lambda rec: rec[1])

k = 0
for path, modified_time in found_files:
    if T is None:
        copied = ""
    else:
        try:
            target_path = os.path.join(T, path.replace("..\\", ""))
            copy2(path, target_path)
            copied = " copied"
        except Exception as exc:
            copied = " copy failed due to " + str(exc)
    print("[%2d]\t%-60s %s%s" % (k, path, modified_time, copied))
    k += 1

if len(found_files) > 0:
    print()

print("\nLatest: %-60s %s" % ( latest_path, latest_time ))
