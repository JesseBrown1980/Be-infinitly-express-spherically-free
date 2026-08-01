"""Create the repo, then harvest the real tree so the README carries measured numbers."""
import json, subprocess, sys

OWNER = "JesseBrown1980"
REPO = "Be-infinitly-express-spherically-free"
DESC = ("Infinite expression of GitHub. The whole account as a sphere - golden-angle "
        "over every direction, not a ring. Every leaf coloured by its own sha, no PID. "
        "A repo that does not answer is counted, never drawn as empty.")


def gh(args, body=None):
    cmd = ["gh", "api"] + args
    if body is not None:
        cmd += ["--input", "-"]
        r = subprocess.run(cmd, input=json.dumps(body), capture_output=True, text=True)
    else:
        r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()[:300]
    return (json.loads(r.stdout) if r.stdout.strip() else {}), None


ep = "repos/%s/%s" % (OWNER, REPO)
meta, err = gh([ep])
if err:
    meta, err = gh(["-X", "POST", "user/repos"],
                   {"name": REPO, "private": False, "auto_init": True, "description": DESC})
    if err:
        sys.exit("create: " + err)
    print("CREATED|%s|json=0" % REPO)
else:
    print("EXISTS|%s|json=0" % REPO)

REPOS = ["two-fixed-points-have-an-interval", "tribute-three-around-a-free-centre",
         "Higgs-Bell-Hilbert-and-Brown-at-the-zero", "identity-kernel-registry",
         "Browns-infinite-play-and-zoom", "free-at-all-levels",
         "does-the-closure-survive-81-levels", "light-boat-engine-ships-with-oils",
         "The-Brown-Light-erdos-Engine-block-powered-by-light",
         "the-browns-solution-to-erods-o0O-nx3-6-for-1-with--1-3",
         "does-2-to-the-n-always-contain-a-digit-2-in-base-3", "one-click",
         "how-and-why-the-system-works", "the-leaves-are-not-the-message",
         "raw-data", REPO]

rows, tot_l, tot_b, miss = [], 0, 0, []
for name in REPOS:
    t, e = gh(["repos/%s/%s/git/trees/HEAD?recursive=1" % (OWNER, name)])
    if e or not t or "tree" not in t:
        miss.append(name)
        print("UNANSWERED|%s|json=0" % name)
        continue
    blobs = [x for x in t["tree"] if x.get("type") == "blob"]
    b = sum(x.get("size", 0) for x in blobs)
    tot_l += len(blobs); tot_b += b
    rows.append((name, len(blobs), b))
    print("BRANCH|%-56s|leaves=%-3d|bytes=%d|json=0" % (name, len(blobs), b))

rows.sort(key=lambda r: -r[1])
print()
print("SPHERE|%s|branches=%d|leaves=%d|bytes=%d|unanswered=%d|json=0"
      % (OWNER, len(rows), tot_l, tot_b, len(miss)))
json.dump({"rows": rows, "leaves": tot_l, "bytes": tot_b, "miss": miss},
          open(__file__.replace("make_repo.py", "measured.json"), "w"))
print("WROTE|measured.json|json=0")
