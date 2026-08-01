"""The tree moves too.

I drew the branches with no sway term, which asserts the tree is static. It is
not. Measured here from tonight's own pushes: the branch colour is derived from
the repository's TREE SHA, so the moment anything is pushed the branch itself
changes colour. Not the leaves. The branch.
"""
import json, subprocess

OWNER = "JesseBrown1980"
REPO = "Be-infinitly-express-spherically-free"
BLO, BHI, LLO, LHI = 16, 240, 32, 224


def gh(a):
    r = subprocess.run(["gh", "api", a], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def cl(v, a, b):
    return max(a, min(b, v))


def lum(c):
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]


def stops(h):
    out = []
    for off in (0, 6):
        c = [cl(int(h[off+2*i:off+2*i+2], 16), BLO, BHI) for i in range(3)]
        L = lum(c)
        out.append(tuple(c) if LLO <= L <= LHI else
                   tuple(int(cl(x*((LLO+LHI)/2)/max(1, L), 0, 255)) for x in c))
    return out


print("=" * 76)
print("THE BRANCH ITSELF CHANGES COLOUR WHEN THE REPO MOVES")
print("=" * 76)

commits = gh("repos/%s/%s/commits?per_page=10" % (OWNER, REPO)) or []
seen = []
for c in commits:
    csha = c["sha"]
    full = gh("repos/%s/%s/commits/%s" % (OWNER, REPO, csha))
    tsha = full["commit"]["tree"]["sha"]
    a, b = stops(tsha)
    seen.append((csha, tsha, a, b, c["commit"]["message"].splitlines()[0][:44]))
    print("COMMIT|%s|tree=%s|stopA=%s|stopB=%s|json=0" % (csha[:12], tsha[:12], a, b))
    print("       %s" % c["commit"]["message"].splitlines()[0][:60])

print()
if len(seen) >= 2:
    n, o = seen[0], seen[1]
    dA = tuple(x - y for x, y in zip(n[2], o[2]))
    dB = tuple(x - y for x, y in zip(n[3], o[3]))
    print("MOTION|from=%s|to=%s|json=0" % (o[0][:12], n[0][:12]))
    print("  stop A  %s  ->  %s     delta %s" % (o[2], n[2], dA))
    print("  stop B  %s  ->  %s     delta %s" % (o[3], n[3], dB))
    print("  tree sha changed: %s" % (o[1] != n[1]))
    print()
    print("  The BRANCH moved, not a leaf. Same repository, minutes apart,")
    print("  a different colour, because the address is the content and the")
    print("  content changed.")

print()
print("=" * 76)
print("EVERY BRANCH, AND HOW RECENTLY IT LAST MOVED")
print("=" * 76)
REPOS = json.load(open(__file__.replace("observers\\motion.py",
                                        "sphere\\measured.json")))["rows"]
rows = []
for name, leaves, byts in REPOS:
    m = gh("repos/%s/%s" % (OWNER, name))
    if not m:
        continue
    rows.append((name, m.get("pushed_at", ""), leaves))
rows.sort(key=lambda r: r[1], reverse=True)
for name, pushed, leaves in rows:
    print("BRANCH|%-54s|pushed_at=%s|leaves=%d|json=0" % (name[:54], pushed, leaves))

print()
print("  No row here is 'never'. Every branch has a last-moved, so every branch")
print("  has a rate. A rate of zero is not present in the data and must not be")
print("  present in the drawing.")
