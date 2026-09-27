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
