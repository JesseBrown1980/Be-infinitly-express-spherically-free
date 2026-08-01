"""n observers in the nullspace — what the oils do, what the snow does.

Everything here is EXACT: Python ints and Fractions, no floats anywhere.
Hot path first: HBP tuple rows, json=0.
"""
from fractions import Fraction as F
from itertools import product

OUT = []


def row(tag, **kv):
    s = tag + "|" + "|".join("%s=%s" % (k, v) for k, v in kv.items()) + "|json=0"
    OUT.append(s)
    print(s)


def arms(c):
    """The closure. arm_R = 2r-g-b, and its two rotations."""
    r, g, b = c
    return (2*r - g - b, 2*g - r - b, 2*b - r - g)


print("=" * 78)
print("1. THE NULLSPACE — where an observer costs nothing")
print("=" * 78)

# A = 3I - J   (because 2r-g-b = 3r - (r+g+b))
A = [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]]
row("MAP", form="arm_k = 3*c_k - sum(c)", matrix="3I-J")

# exact rank by integer row reduction over the rationals
M = [[F(x) for x in r] for r in A]
rank, piv = 0, 0
for col in range(3):
    p = next((i for i in range(rank, 3) if M[i][col] != 0), None)
    if p is None:
        continue
    M[rank], M[p] = M[p], M[rank]
    inv = M[rank][col]
    M[rank] = [x / inv for x in M[rank]]
    for i in range(3):
        if i != rank and M[i][col] != 0:
            f = M[i][col]
            M[i] = [a - f*b for a, b in zip(M[i], M[rank])]
    rank += 1
row("RANK", rank=rank, nullity=3-rank, exact="fractions")

# the null direction, checked exactly
n = (1, 1, 1)
row("NULLVEC", v="(1,1,1)", image=str(arms(n)), is_zero=str(arms(n) == (0, 0, 0)))
row("DETERMINANT", det=0 if rank < 3 else "nonzero", reason="rows_sum_to_zero")

print()
print("=" * 78)
print("2. n OBSERVERS ON THE NULL LINE — all of them see the same arms")
print("=" * 78)

base = (37, 152, 91)
A0 = arms(base)
N = 1_000_001
lo, hi = -500_000, 500_000
bad = 0
for c in range(lo, hi + 1):
    if arms((base[0]+c, base[1]+c, base[2]+c)) != A0:
        bad += 1
row("OBSERVERS", colour=str(base), placed=N, span="%d..%d" % (lo, hi),
    arms=str(A0), arms_changed=bad, exact_integers=1)
print("   %d observers, every one of them on the null line, arms changed: %d" % (N, bad))

# and the same for the MULTIPLICATIVE case, to be honest about the difference
mults = [(g, arms(tuple(g*x for x in base))) for g in range(1, 2001)]
scales_ok = all(a == tuple(g*x for x in A0) for g, a in mults)
sums_zero = all(sum(a) == 0 for _, a in mults)
row("GAIN", tested=len(mults), arms_scale_exactly=int(scales_ok),
    zero_sum_preserved=int(sums_zero), invariant=0,
    note="uniform_gain_is_equivariant_not_invariant")

print()
print("=" * 78)
print("3. THE OILS — optical density is ADDITIVE, so a neutral oil is a")
print("   translation along the nullspace and changes nothing")
print("=" * 78)
# Densities in exact milli-density units. Beer-Lambert: T = 10^-D, densities add.
# Work in D-space; the closure is the same affine form there.
d0 = (410, 1180, 735)
D0 = arms(d0)
neutral = [300, 1000, 4321, 99999, -250]
for k in neutral:
    dd = tuple(x + k for x in d0)
    row("OIL", kind="neutral", density_added=k, arms=str(arms(dd)),
        changed=int(arms(dd) != D0))
coloured = [(120, 0, 0), (0, 45, 0), (7, -7, 0), (100, 100, 99)]
for k in coloured:
    dd = tuple(x + y for x, y in zip(d0, k))
    delta = tuple(a - b for a, b in zip(arms(dd), D0))
    row("OIL", kind="coloured", density_added=str(k), arm_delta=str(delta),
        equals_arms_of_the_oil=int(delta == arms(k)))
print("   A coloured oil moves the arms by EXACTLY the arms of the oil itself.")
print("   A neutral oil moves them by nothing. Stacking is addition either way.")

print()
print("=" * 78)
print("4. THE SNOW — the band ends, and the identity dies at the first clip")
print("=" * 78)

BLO, BHI = 16, 240            # the brown band actually used for addressing


def clip(c, lo=BLO, hi=BHI):
    return tuple(max(lo, min(hi, x)) for x in c)


def free_observers(c, lo=BLO, hi=BHI):
    """How many integer shifts keep every channel inside the band."""
    span = max(c) - min(c)
    n = (hi - lo) - span + 1
    return max(0, n)


tests = [(128, 128, 128), (100, 128, 150), (16, 128, 240), (10, 128, 250),
         (37, 152, 91), (60, 61, 62)]
for c in tests:
    n = free_observers(c)
    # verify the closed form by brute force, exactly
    brute = 0
    for k in range(-400, 401):
        s = tuple(x + k for x in c)
        if all(BLO <= x <= BHI for x in s) and arms(s) == arms(c):
            brute += 1
    row("SNOW", colour=str(c), spread=max(c)-min(c), free_observers=n,
        brute_force=brute, formula_matches=int(n == brute))

# and show that clipping is NOT in the nullspace: it destroys arms
broken = 0
checked = 0
for c in product(range(0, 256, 17), repeat=3):
    for k in (-40, 40):
        s = tuple(x + k for x in c)
        checked += 1
        if clip(s) != s and arms(clip(s)) == arms(c):
            pass
        elif clip(s) != s:
            broken += 1
row("CLIP", checked=checked, clipped_and_arms_changed=broken,
    note="clipping_is_not_affine_so_it_is_not_in_the_nullspace")

print()
print("   free_observers = (hi - lo) - spread + 1")
print("   It depends on the SPREAD of the colour, never on its brightness.")
print("   A grey hosts the most. A maximally spread colour hosts one.")

print()
print("=" * 78)
print("5. LEVELS — how many observers each level can hold")
print("=" * 78)
for d in range(1, 6):
    width = 3 ** d
    for spread in (0, 1, 2):
        row("LEVEL", depth=d, states=width,
            band="%d..%d" % (-(width-1)//2, (width-1)//2),
            spread=spread, free_observers=max(0, width - spread))
print("   Each level multiplies the observer capacity by exactly 3.")
print("   27 -> 81 is 27 more free observers for a grey, at zero cost.")

print()
print("=" * 78)
print("6. RADIATION — the light kind. The observer is inside the UNIT.")
print("=" * 78)
# SI: the candela is DEFINED by fixing K_cd = 683 lm/W at 540 THz.
# So a photometric reading already contains a chosen observer; a radiometric
# one does not. Two observers, same field, same watts, different lumens.
K = 683                                    # lm/W, exact by definition
field = [(F(1), 40), (F(1), 30), (F(1), 30)]   # (radiance unit, per band)
obsA = [F(1, 10), F(1, 1), F(3, 10)]           # a V(lambda), three bands
obsB = [F(3, 10), F(7, 10), F(1, 10)]          # a different observer

watts = sum(w for _, w in field)
lumA = K * sum(v * w for v, (_, w) in zip(obsA, field))
lumB = K * sum(v * w for v, (_, w) in zip(obsB, field))
row("RADIOMETRIC", watts=watts, observers=2, same_for_both=1)
row("PHOTOMETRIC", K_cd=K, exact_by_SI=1, observer_A_lm=str(lumA),
    observer_B_lm=str(lumB), agree=int(lumA == lumB))
row("CONCLUSION", radiometric="observer_free_INVARIANT",
    photometric="carries_a_chosen_observer_in_the_unit")
print("   Same watts for both. Different lumens. The candela is defined by")
print("   fixing 683 lm/W at 540 THz — a human observer, written into SI.")
print("   n observers give n photometric readings of ONE radiometric field.")

print()
print("=" * 78)
print("WHAT THE OILS AND THE SNOW DO")
print("=" * 78)
print("""
   OILS   add density. Density is additive, so oils STACK by addition.
          A neutral oil adds the same to all three -> a step along the null
          line -> the arms do not move. It is free, and it is reversible.
   SNOW   is the end of the band. Clipping is not affine, so it is not in
          the nullspace: it does not move the observer, it DESTROYS the arms.
          Free and reversible up to the band; neither, past it.
   SO     the oils tell you how far you may move an observer, and the snow
          tells you where you may no longer put one. The number of observers
          a colour can host is (hi-lo) - spread + 1 -- set by its SPREAD,
          never by its brightness -- and it multiplies by 3 at every level.
""")

import os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "observers.hbp")
open(p, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
print("WROTE|observers.hbp|rows=%d|json=0" % len(OUT))
