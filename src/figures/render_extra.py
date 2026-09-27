"""render_extra.py - PyMOL renders of the carriers for Figure 1 (uses render3d._run).

B...B pairs across the four-membered rings of the BN cage (about 1.86 A) are
unbonded before drawing: PyMOL's distance-based bonding would otherwise show the
very contacts that the paper explains are not bonds."""
import render3d as R


def cage(xyz, png, size=(1200, 1200)):
    body = f"""
    cmd.load({R._q(xyz)}, 'm')
    cmd.unbond('m and elem B', 'm and elem B')
    cmd.unbond('m and elem N', 'm and elem N')
    cmd.hide('everything')
    cmd.set_color('cB', [0.96, 0.71, 0.66]); cmd.color('cB', 'elem B')
    cmd.set_color('cN', [0.20, 0.33, 0.85]); cmd.color('cN', 'elem N')
    cmd.set('sphere_scale', 0.24); cmd.set('stick_radius', 0.12)
    cmd.show('sticks'); cmd.show('spheres')
    cmd.set('depth_cue', 1)
    cmd.orient('m'); cmd.turn('x', 25); cmd.turn('y', 20)
    cmd.zoom('m', 0.8)
    cmd.png({R._q(png)}, width={size[0]}, height={size[1]}, dpi=600, ray=1)
    """
    R._run(body)


def slab(xyz, png, size=(1500, 1000)):
    body = f"""
    cmd.load({R._q(xyz)}, 'm')
    cmd.unbond('m and elem O', 'm and elem O')
    cmd.unbond('m and elem C', 'm and elem C')
    cmd.unbond('m and elem Ti', 'm and elem Ti')
    cmd.hide('everything')
    cmd.set_color('cTi', [0.62, 0.68, 0.80]); cmd.color('cTi', 'elem Ti')
    cmd.set_color('cC', [0.33, 0.35, 0.39]); cmd.color('cC', 'elem C')
    cmd.set_color('cO', [0.86, 0.20, 0.18]); cmd.color('cO', 'elem O')
    cmd.set('sphere_scale', 0.26); cmd.set('stick_radius', 0.11)
    cmd.show('sticks'); cmd.show('spheres')
    cmd.set('depth_cue', 1); cmd.set('fog_start', 0.45)
    cmd.set_view([1,0,0, 0,1,0, 0,0,1, 0,0,-60, 6.8,4.0,0, 40,80,0])
    cmd.turn('x', -72); cmd.turn('y', 18)
    cmd.zoom('m', 0.3)
    cmd.png({R._q(png)}, width={size[0]}, height={size[1]}, dpi=600, ray=1)
    """
    R._run(body)


def bonded(xyz, png, forbidden, size=(1200, 1100), tilt=20, turn_y=0):
    """Carrier drawn with the audit's own bonds (1.15 x covalent radii, B...B / N...N
    four-ring diagonals excluded); bonds the material cannot contain in red."""
    import sys
    from itertools import combinations
    from pathlib import Path
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from audit_carriers import COV, read_xyz
    el, x = read_xyz(xyz)
    pairs = [(i, j) for i, j in combinations(range(len(el)), 2)
             if not (el[i] == el[j] == "Ti") and np.linalg.norm(x[i] - x[j]) < 1.15 * (COV[el[i]] + COV[el[j]])]
    nb = {i: set() for i in range(len(el))}
    for i, j in pairs:
        nb[i].add(j); nb[j].add(i)
    keep, bad = [], []
    for i, j in pairs:
        a, b = sorted((el[i], el[j]))
        if a == b and a in ("B", "N") and len({k for k in nb[i] & nb[j] if el[k] != a}) >= 2:
            continue                                   # 4-ring diagonal, not a bond
        keep.append((i, j))
        if f"{a}-{b}" in forbidden:
            bad.append((i, j))
    good = [b for b in keep if b not in bad]
    body = f"""
    cmd.load({R._q(xyz)}, 'm')
    cmd.load({R._q(xyz)}, 'f')
    cmd.unbond('m', 'm'); cmd.unbond('f', 'f')
    for i, j in {good}:
        cmd.bond('m and index %d' % (i + 1), 'm and index %d' % (j + 1))
    for i, j in {bad}:
        cmd.bond('f and index %d' % (i + 1), 'f and index %d' % (j + 1))
    cmd.hide('everything')
    cmd.set_color('cB', [0.96, 0.71, 0.66]); cmd.color('cB', 'm and elem B')
    cmd.set_color('cN', [0.20, 0.33, 0.85]); cmd.color('cN', 'm and elem N')
    cmd.set_color('cC', [0.33, 0.35, 0.39]); cmd.color('cC', 'm and elem C')
    cmd.set_color('cO', [0.86, 0.20, 0.18]); cmd.color('cO', 'm and elem O')
    cmd.set_color('cTi', [0.62, 0.68, 0.80]); cmd.color('cTi', 'm and elem Ti')
    cmd.color('white', 'm and elem H')
    cmd.set('sphere_scale', 0.2, 'm'); cmd.set('stick_radius', 0.1, 'm')
    cmd.show('sticks', 'm'); cmd.show('spheres', 'm')
    cmd.set_color('bad', [0.98, 0.66, 0.05]); cmd.color('bad', 'f')
    cmd.set('stick_radius', 0.17, 'f')
    cmd.show('sticks', 'f')
    cmd.set('depth_cue', 1)
    cmd.orient('m'); cmd.turn('x', {tilt}); cmd.turn('y', {turn_y})
    cmd.zoom('m', 0.8)
    cmd.png({R._q(png)}, width={size[0]}, height={size[1]}, dpi=600, ray=1)
    """
    R._run(body)
    return len(keep), len(bad)
