# coding: utf-8
"""
Helper utilities for pyLessSDK skill validation.
These functions can be used in generated code to validate simulation configurations.
"""


def check_ortho_spp(image_width, image_height, sub_region_width, sub_region_height, sample_per_pixel):
    """
    Check if orthographic sensor has sufficient spatial sampling density.
    Recommends at least 64 samples per square meter.

    Returns (is_ok, actual_density, recommended_spp)
    """
    pixel_area = (sub_region_width / image_width) * (sub_region_height / image_height)  # m² per pixel
    density = sample_per_pixel / pixel_area  # samples per m²
    if density >= 64:
        return True, density, sample_per_pixel
    recommended_spp = max(64, int(64 * pixel_area))
    return False, density, recommended_spp


def check_band_consistency(sensor_bands_str, ats_percentage_str=None, op_items=None):
    """
    Validate that band counts are consistent across sensor, atmosphere, and optical properties.

    :param sensor_bands_str: Sensor spectral bands string, e.g. "680:1,550:1,450:1"
    :param ats_percentage_str: Sky-to-total ratio string, e.g. "0.1,0.1,0.1"
    :param op_items: List of (name, value_str) tuples for optical properties
    :return: List of error messages (empty if all ok)
    """
    errors = []
    sensor_count = len(sensor_bands_str.split(","))

    if ats_percentage_str:
        ats_count = len(ats_percentage_str.split(","))
        if ats_count != sensor_count:
            errors.append(
                f"Sky-to-total ratio has {ats_count} bands but sensor has {sensor_count}. "
                f"Fix: pad with ',0' or trim to match."
            )

    if op_items:
        for name, value_str in op_items:
            groups = value_str.split(";")
            for i, group in enumerate(groups):
                group_count = len(group.split(","))
                if group_count != sensor_count:
                    group_names = ["front_reflectance", "back_reflectance", "transmittance"]
                    gname = group_names[i] if i < len(group_names) else f"group_{i}"
                    errors.append(
                        f"OpticalItem '{name}' {gname} has {group_count} bands "
                        f"but sensor has {sensor_count}."
                    )

    return errors


def check_turbid_within_bounds(place_x, place_y, obj_bbox_half_x, obj_bbox_half_y,
                                extent_width, extent_height):
    """
    Check if a turbid medium object placed at (place_x, place_y) stays within scene bounds.
    obj_bbox_half_x/y: half-width of the object bounding box in x/y direction.

    Returns (is_ok, message)
    """
    min_x = place_x - obj_bbox_half_x
    max_x = place_x + obj_bbox_half_x
    min_y = place_y - obj_bbox_half_y
    max_y = place_y + obj_bbox_half_y

    if min_x < 0 or max_x > extent_width or min_y < 0 or max_y > extent_height:
        return False, (
            f"Object at ({place_x}, {place_y}) with bbox half-size "
            f"({obj_bbox_half_x}, {obj_bbox_half_y}) exceeds scene bounds "
            f"(0,0)-({extent_width},{extent_height}). "
            f"Actual extent: ({min_x:.2f},{min_y:.2f})-({max_x:.2f},{max_y:.2f})"
        )
    return True, "OK"


def compute_turbid_lai(crown_volume, leaf_density, num_trees, scene_area):
    """
    Compute LAI for turbid medium scenes.
    LAI = crown_volume * leaf_density * num_trees / scene_area

    :param crown_volume: Volume of a single crown (m³)
    :param leaf_density: Leaf area density (m²/m³)
    :param num_trees: Number of trees
    :param scene_area: Scene area (m²), i.e. extent_width * extent_height
    :return: LAI value
    """
    return crown_volume * leaf_density * num_trees / scene_area


def suggest_spp(scene_width, scene_height, image_width, image_height, min_density=64):
    """
    Suggest sample_per_pixel for orthographic sensor based on minimum per-m² density.

    :param scene_width: Scene extent width (m)
    :param scene_height: Scene extent height (m)
    :param image_width: Image width (pixels)
    :param image_height: Image height (pixels)
    :param min_density: Minimum samples per m² (default 64)
    :return: Suggested sample_per_pixel value
    """
    pixel_area = (scene_width / image_width) * (scene_height / image_height)
    spp = int(min_density * pixel_area)
    return max(spp, 16)  # at least 16
