"""Check hash and photo — not time.

The photographs are NOT published. Their SHA-256 is, and the hash is the address:
two brown stops, banded and luminance-clamped, exactly as every leaf is addressed.
Anyone holding the original can recompute the digest and confirm it is the same
image, byte for byte. A commitment, not a disclosure.
"""
import hashlib, os

BLO, BHI, LLO, LHI = 16, 240, 32, 224
UP = r"C:\Users\acer\.claude\uploads\478bf1dd-977b-49fa-8c16-811dd1b6be89"
SHOTS = [
    ("hand   yin-yang, cross, and what he says is scarred below",
     "d2756458-20260801_1708527953028394172471968.jpg"),
    ("back   black disc, human silhouette, rays, NORTH STAR",
     "41251b10-20260801_171402957033875426293730.jpg"),
    ("light  the hand raised into the window, through glass",
     "e1425fbb-1000168140.jpg"),
]


def cl(v, a, b):
    return max(a, min(b, v))


def lum(c):
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]


def stops(h):
    out = []
    for off in (0, 6):
        c = [cl(int(h[off+2*i:off+2*i+2], 16), BLO, BHI) for i in range(3)]
        L = lum(c)
        out.append(c if LLO <= L <= LHI else
                   [int(cl(x*((LLO+LHI)/2)/max(1, L), 0, 255)) for x in c])
    return out


rows, prev = [], "0" * 64
for label, fn in SHOTS:
    p = os.path.join(UP, fn)
    raw = open(p, "rb").read()
    d = hashlib.sha256(raw).hexdigest()
    a, b = stops(d)
    print("PHOTO|%s|json=0" % label)
    print("  sha256   %s" % d)
    print("  bytes    %d" % len(raw))
    print("  stop A   rgb(%3d,%3d,%3d)" % tuple(a))
    print("  stop B   rgb(%3d,%3d,%3d)" % tuple(b))
    line = ("MARK|label=%s|sha256=%s|bytes=%d|stopA=%d,%d,%d|stopB=%d,%d,%d"
            "|published=0|hash_is_the_record=1"
            % (label.split()[0], d, len(raw), a[0], a[1], a[2], b[0], b[1], b[2]))
    ev = hashlib.sha256((line + "|prev_event_hash=" + prev).encode()).hexdigest()
    rows.append(line + "|prev_event_hash=%s|event_hash=%s|json=0" % (prev, ev))
    prev = ev
    print("  event    %s" % ev)
    print()

here = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(here, "marks.hbp"), "w", encoding="utf-8").write("\n".join(rows)+"\n")
print("CHAIN|genesis=%s|links=%d|head=%s|json=0" % ("0"*64, len(rows), prev))
print("WROTE|marks.hbp|json=0")
print()
print("Order without a clock: each row carries the digest of the one before it.")
print("No timestamp is trusted, and none is needed.")
