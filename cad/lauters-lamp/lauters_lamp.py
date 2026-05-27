from math import atan2, cos, degrees, pi, sin, sqrt

from build123d import (
    Align,
    Box,
    BuildPart,
    Color,
    Compound,
    Cone,
    Cylinder,
    Location,
    Mode,
    Plane,
    Sphere,
    Torus,
)


# Parametric visual CAD model of the IKEA LAUTERS floor lamp.
# Units: millimeters. Origin: floor center. +Z: upward.


HEIGHT_MIN = 1190.0
HEIGHT_MAX = 1510.0
SHADE_DIAMETER = 370.0
SHADE_HEIGHT = 267.0
BASE_DIAMETER = 620.0
CORD_LENGTH = 3500.0


ASH = Color(0.86, 0.58, 0.32, 1.0)
END_GRAIN = Color(0.72, 0.44, 0.22, 1.0)
SHADE_WHITE = Color(0.96, 0.94, 0.88, 0.42)
WARM_WHITE = Color(1.0, 0.89, 0.58, 0.75)
METAL = Color(0.72, 0.72, 0.68, 1.0)
CORD = Color(0.90, 0.88, 0.84, 1.0)
DARK_MARK = Color(0.25, 0.16, 0.10, 1.0)


def _label(shape, label, color=None):
    shape.label = label
    if color is not None:
        shape.color = color
    return shape


def _between(shape, start, end):
    """Place a Z-axis primitive between two 3D points."""
    sx, sy, sz = start
    ex, ey, ez = end
    dx, dy, dz = ex - sx, ey - sy, ez - sz
    center = ((sx + ex) / 2, (sy + ey) / 2, (sz + ez) / 2)
    return Location(Plane(origin=center, z_dir=(dx, dy, dz))) * shape


def _round_rod(start, end, radius, label, color):
    sx, sy, sz = start
    ex, ey, ez = end
    length = sqrt((ex - sx) ** 2 + (ey - sy) ** 2 + (ez - sz) ** 2)
    return _label(_between(Cylinder(radius, length), start, end), label, color)


def _rect_leg(start, end, label):
    sx, sy, sz = start
    ex, ey, ez = end
    length = sqrt((ex - sx) ** 2 + (ey - sy) ** 2 + (ez - sz) ** 2)
    leg = _between(Box(28, 36, length, align=(Align.CENTER, Align.CENTER, Align.CENTER)), start, end)
    return _label(leg, label, ASH)


def _hollow_cylinder(outer_radius, inner_radius, height, label, color):
    with BuildPart() as part:
        Cylinder(outer_radius, height, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        Cylinder(inner_radius, height + 8, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.SUBTRACT)
    return _label(part.part, label, color)


def _cable_segment(start, end, radius, label):
    seg = _round_rod(start, end, radius, label, CORD)
    return seg


def _make_cord(height):
    hub_z = 650.0
    top_z = height - SHADE_HEIGHT - 32.0
    pts = [
        (24, -20, top_z),
        (48, -34, 1020),
        (34, -28, 760),
        (20, -18, hub_z),
        (12, -88, 610),
        (38, -132, 590),
        (82, -105, 610),
        (38, -72, 625),
        (0, -22, 605),
        (115, -238, 28),
        (312, -320, 12),
        (610, -324, 10),
        (920, -324, 10),
    ]
    parts = []
    for idx, (a, b) in enumerate(zip(pts[:-1], pts[1:]), start=1):
        parts.append(_cable_segment(a, b, 4.0, f"white_power_cord_segment_{idx:02d}"))
    for idx, p in enumerate(pts[1:-1], start=1):
        parts.append(_label(Location(p) * Sphere(4.2), f"cord_smooth_bend_{idx:02d}", CORD))
    return parts


def _make_lamp(height=HEIGHT_MAX):
    shade_center_z = height - SHADE_HEIGHT / 2.0
    shade_bottom_z = height - SHADE_HEIGHT
    hub_z = 650.0
    foot_r = BASE_DIAMETER / 2.0
    shoulder_r = 96.0

    parts = []

    shade = _hollow_cylinder(SHADE_DIAMETER / 2.0, SHADE_DIAMETER / 2.0 - 5.0, SHADE_HEIGHT, "translucent_white_fabric_cylindrical_shade", SHADE_WHITE)
    parts.append(Location((0, 0, shade_center_z)) * shade)
    for name, z in [("upper_shade_rim", height), ("lower_shade_rim", shade_bottom_z)]:
        parts.append(_label(Location((0, 0, z)) * Torus(SHADE_DIAMETER / 2.0 - 5.0, 5.5), name, SHADE_WHITE))

    parts.append(_label(Location((0, 0, shade_bottom_z + 42)) * Cylinder(24, 54), "white_socket_collar", METAL))
    parts.append(_label(Location((0, 0, shade_bottom_z + 88)) * Sphere(44), "opal_white_e26_globe_bulb", WARM_WHITE))
    parts.append(_label(Location((0, 0, shade_bottom_z + 42)) * Cylinder(16, 90), "internal_lamp_threaded_stem", METAL))

    lower_tube_top = hub_z + 90
    upper_tube_bottom = hub_z + 20
    parts.append(_label(Location((0, 0, (lower_tube_top + 32) / 2)) * Cylinder(16, lower_tube_top - 32), "fixed_ash_center_tube", ASH))
    parts.append(_label(Location((0, 0, (upper_tube_bottom + shade_bottom_z + 70) / 2)) * Cylinder(12, shade_bottom_z + 70 - upper_tube_bottom), "sliding_height_adjustment_tube", ASH))

    parts.append(_label(Location((0, 0, hub_z)) * Cylinder(88, 44), "round_tripod_hub_plate", ASH))
    parts.append(_label(Location((0, 0, hub_z + 26)) * Cylinder(58, 18), "raised_center_boss", END_GRAIN))
    parts.append(_label(Location((0, 0, hub_z - 28)) * Cylinder(42, 18), "lower_cord_storage_spool", END_GRAIN))
    parts.append(_label(Location((0, 0, hub_z - 62)) * Cylinder(54, 10), "bottom_cord_storage_disc", ASH))
    parts.append(_label(Location((0, 0, hub_z - 46)) * Cylinder(24, 34), "spool_core", ASH))

    # A clamp block and thumb screw make the height-adjustment function visible.
    parts.append(_label(Location((0, -70, hub_z + 15)) * Box(70, 28, 34), "sliding_tube_clamp_block", ASH))
    parts.append(_label(_round_rod((0, -90, hub_z + 15), (0, -138, hub_z + 15), 8, "metal_height_lock_screw", METAL), "metal_height_lock_screw", METAL))
    parts.append(_label(Location((0, -154, hub_z + 15), (90, 0, 0)) * Cylinder(20, 12), "round_wood_thumb_knob", END_GRAIN))
    parts.append(_label(Location((0, -166, hub_z + 15), (90, 0, 0)) * Cylinder(9, 4), "knob_center_cap", DARK_MARK))

    for i in range(3):
        angle = 2 * pi * i / 3.0 + pi / 2.0
        foot = (foot_r * cos(angle), foot_r * sin(angle), 18)
        shoulder = (shoulder_r * cos(angle), shoulder_r * sin(angle), hub_z - 18)
        leg = _rect_leg(shoulder, foot, f"tapered_ash_tripod_leg_{i + 1}")
        parts.append(leg)
        parts.append(_label(Location((foot[0], foot[1], 8), (0, 0, degrees(angle))) * Box(52, 36, 16), f"angled_flat_foot_pad_{i + 1}", END_GRAIN))
        parts.append(_label(Location((shoulder[0], shoulder[1], hub_z + 4)) * Cylinder(14, 18), f"leg_pivot_pin_{i + 1}", METAL))

    for i in range(3):
        angle = 2 * pi * i / 3.0 + pi / 2.0
        brace_start = (56 * cos(angle), 56 * sin(angle), hub_z - 42)
        brace_end = (182 * cos(angle), 182 * sin(angle), 260)
        parts.append(_round_rod(brace_start, brace_end, 8, f"inner_ash_support_strut_{i + 1}", ASH))

    # Travel marks make the min/max adjustment range legible in CAD.
    parts.append(_label(Location((-24, 0, HEIGHT_MIN - SHADE_HEIGHT - 18)) * Box(4, 24, 7), "minimum_height_mark_on_sliding_tube", DARK_MARK))
    parts.append(_label(Location((-24, 0, HEIGHT_MAX - SHADE_HEIGHT - 18)) * Box(4, 24, 7), "maximum_height_mark_on_sliding_tube", DARK_MARK))
    parts.append(_round_rod((-42, 0, HEIGHT_MIN - SHADE_HEIGHT), (-42, 0, HEIGHT_MAX - SHADE_HEIGHT), 2.0, "visible_320mm_adjustment_travel_reference", METAL))

    parts.extend(_make_cord(height))

    assembly = Compound(children=parts, label=f"lauters_floor_lamp_{int(height)}mm_height")
    assembly.color = Color(0.8, 0.8, 0.8, 1.0)
    return assembly


def gen_step():
    return _make_lamp(HEIGHT_MAX)


def gen_min_height_step():
    return _make_lamp(HEIGHT_MIN)
