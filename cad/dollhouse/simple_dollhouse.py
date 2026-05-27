from build123d import (
    Align,
    Box,
    Color,
    Compound,
    Cylinder,
    Location,
)
from math import atan2, degrees, sqrt


def _box(label, size, loc, color):
    part = Box(*size, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(Location(loc))
    part.label = label
    part.color = Color(*color)
    return part


def _rotated_box(label, size, loc, rotation, color):
    part = Box(*size, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(Location(loc, rotation))
    part.label = label
    part.color = Color(*color)
    return part


def gen_step():
    # Units: mm. Origin at house center on the floor plane; +Z is up.
    house_w = 90.0
    house_d = 62.0
    wall_h = 70.0
    wall_t = 4.0
    roof_rise = 30.0
    floor_t = 4.0

    parts = [
        _box("floor_slab", (house_w + 8, house_d + 8, floor_t), (0, 0, floor_t / 2), (0.72, 0.57, 0.38, 1.0)),
        _box("back_wall", (house_w, wall_t, wall_h), (0, house_d / 2 - wall_t / 2, floor_t + wall_h / 2), (0.94, 0.82, 0.62, 1.0)),
        _box("left_wall", (wall_t, house_d, wall_h), (-house_w / 2 + wall_t / 2, 0, floor_t + wall_h / 2), (0.94, 0.82, 0.62, 1.0)),
        _box("right_wall", (wall_t, house_d, wall_h), (house_w / 2 - wall_t / 2, 0, floor_t + wall_h / 2), (0.94, 0.82, 0.62, 1.0)),
        _box("center_floor", (house_w - 8, house_d - 6, 3.0), (0, 0, floor_t + 34.0), (0.78, 0.65, 0.46, 1.0)),
        _box("front_door", (20.0, 2.8, 36.0), (0, -house_d / 2 - 1.4, floor_t + 18.0), (0.36, 0.18, 0.09, 1.0)),
        _box("left_window_frame", (16.0, 3.0, 18.0), (-27.0, -house_d / 2 - 1.5, floor_t + 46.0), (0.18, 0.38, 0.58, 1.0)),
        _box("right_window_frame", (16.0, 3.0, 18.0), (27.0, -house_d / 2 - 1.5, floor_t + 46.0), (0.18, 0.38, 0.58, 1.0)),
        _box("left_window_glass", (11.0, 3.4, 13.0), (-27.0, -house_d / 2 - 1.8, floor_t + 46.0), (0.58, 0.82, 0.96, 0.72)),
        _box("right_window_glass", (11.0, 3.4, 13.0), (27.0, -house_d / 2 - 1.8, floor_t + 46.0), (0.58, 0.82, 0.96, 0.72)),
    ]

    roof_w = house_w + 14.0
    roof_d = house_d + 12.0
    roof_t = 5.0
    half_roof_w = roof_w / 2
    roof_angle = degrees(atan2(roof_rise, half_roof_w))
    roof_panel_len = sqrt(half_roof_w**2 + roof_rise**2)
    roof_center_z = floor_t + wall_h + roof_rise / 2
    left_roof = _rotated_box(
        "left_roof_panel",
        (roof_panel_len, roof_d, roof_t),
        (-half_roof_w / 2, 0, roof_center_z),
        (0, -roof_angle, 0),
        (0.58, 0.13, 0.10, 1.0),
    )
    right_roof = _rotated_box(
        "right_roof_panel",
        (roof_panel_len, roof_d, roof_t),
        (half_roof_w / 2, 0, roof_center_z),
        (0, roof_angle, 0),
        (0.58, 0.13, 0.10, 1.0),
    )
    parts.extend([left_roof, right_roof])

    chimney = _box(
        "chimney",
        (12.0, 12.0, 30.0),
        (26.0, 10.0, floor_t + wall_h + roof_rise + 5.0),
        (0.45, 0.17, 0.12, 1.0),
    )
    parts.append(chimney)

    knob = Cylinder(1.8, 1.2, align=(Align.CENTER, Align.CENTER, Align.CENTER)).moved(
        Location((7.0, -house_d / 2 - 3.0, floor_t + 18.0), (90, 0, 0))
    )
    knob.label = "round_door_knob"
    knob.color = Color(0.95, 0.78, 0.28, 1.0)
    parts.append(knob)

    model = Compound(obj=parts, children=parts, label="simple_little_dollhouse")
    return model
