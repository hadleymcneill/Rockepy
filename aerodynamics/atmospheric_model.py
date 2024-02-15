"""
This file provides the functions to accurately model atmospheric effects on a rocket's flight path.
"""

import numpy as np


def atmospheric_density(altitude):
    """
    Calculates density for altitudes from sea level through 1000 km using exponential interpolation
    of the 1976 US Standard Atmosphere model.

    Args:
        altitude (float): Altitude above sea level (km).

    Returns:
        float: Atmospheric density (kg/m^3).
    """

    # Reference altitudes (km):
    h = np.array([
        0, 25, 30, 40, 50, 60, 70,
        80, 90, 100, 110, 120, 130, 140,
        150, 180, 200, 250, 300, 350, 400,
        450, 500, 600, 700, 800, 900, 1000
    ])

    # Corresponding densities (kg/m^3) from USSA76:
    reference_density = np.array([
        1.225, 4.008e-2, 1.841e-2, 3.996e-3, 1.027e-3, 3.097e-4, 8.283e-5,
        1.846e-5, 3.416e-6, 5.606e-7, 9.708e-8, 2.222e-8, 8.152e-9, 3.831e-9,
        2.076e-9, 5.194e-10, 2.541e-10, 6.073e-11, 1.916e-11, 7.014e-12, 2.803e-12,
        1.184e-12, 5.215e-13, 1.137e-13, 3.070e-14, 1.136e-14, 5.759e-15, 3.561e-15
    ])

    # Scale heights (km):
    H = np.array([
        7.310, 6.427, 6.546, 7.360, 8.342, 7.583, 6.661,
        5.927, 5.533, 5.703, 6.782, 9.973, 13.243, 16.322,
        21.652, 27.974, 34.934, 43.342, 49.755, 54.513, 58.019,
        60.980, 65.654, 76.377, 100.587, 147.203, 208.020
    ])

    # Handle altitudes outside the range:
    if altitude > 1000 or altitude < 0:
        return 0

    # Determine the interpolation interval:
    i = np.searchsorted(h, altitude) - 1
    if altitude == 1000:  # Edge case
        i = 26

    # Exponential interpolation:
    density = reference_density[i] * np.exp(-(altitude - h[i]) / H[i])
    return density


def wind_model(altitude, condition="None"):
    """
    Calculates the wind velocity vector at a given altitude above sea level.

    Wind data taken from:
    "SMARTS Modeling of Solar Spectra at Stratospheric
    Altitude and Influence on Performance of Selected
    III-V Solar Cells
    Moritz Limpinsel, Member, IEEE, Dawei Kuo, and Aarohi Vijh, Senior Member, IEEE"

    Args:
        altitude (float): Altitude above sea level in (km).
        condition (str): Wind condition as "None", "Light", "Moderate", "Strong", or "Very Strong".

    Returns:
        np.array: Wind velocity vector [vx, vy, 0] in km/s.
    """
    # Scale factors for different wind conditions
    condition_scale = {
        "None": 0,
        "Light": 0.5,
        "Moderate": 1,
        "Strong": 1.5,
        "Very Strong": 2
    }

    # Scale the wind speed based on the wind condition
    scale_factor = condition_scale.get(condition, 0)

    # Handle altitudes outside the range:
    if altitude > 100 or altitude < 0:
        return np.array([0, 0, 0])

    # Define altitude layers (km) and corresponding wind speeds (m/s)
    # Note: Wind speeds are very low in km/s, so we're still defining these in m/s but will convert output to km/s
    altitude_layers = [0, 1, 3, 5, 10, 15, 18, 20, 30, 50, 70, 80, 90, 100, 120]
    wind_speeds_mps = [5, 6, 10, 15, 20, 18, 10, 1, 15, 40, 67, 40, 25, 35, 10]

    # Wind generally flows in one direction, but can vary drastically locally, particularly at lower altitudes.
    wind_directions = [90, 45, 0, 270, 225, 180, 135, 90, 45, 0, 0, 0, 0, 0, 0]

    # Defines wind direction +/- variability (deg) from the base direction
    direction_variability = 30

    # Find the current layer
    layer_index = np.searchsorted(altitude_layers, altitude, side='right') - 1
    layer_index = max(0, min(layer_index, len(altitude_layers) - 2))

    # Linearly interpolate wind speed and base direction between layers
    interp_factor = (altitude - altitude_layers[layer_index]) / (
                altitude_layers[layer_index + 1] - altitude_layers[layer_index])
    wind_speed = wind_speeds_mps[layer_index] + (
                wind_speeds_mps[layer_index + 1] - wind_speeds_mps[layer_index]) * interp_factor
    base_wind_direction = wind_directions[layer_index] + (
                wind_directions[layer_index + 1] - wind_directions[layer_index]) * interp_factor

    # Apply semi-random adjustment to the wind direction within the defined variability range (normal distribution)
    adjusted_wind_direction = base_wind_direction + np.random.normal(0, direction_variability)

    # Convert adjusted wind direction and speed to a vector, converting speed from m/s to km/s
    wind_direction_rad = np.radians(adjusted_wind_direction)
    vx = (wind_speed * np.cos(wind_direction_rad)) / 1000
    vy = (wind_speed * np.sin(wind_direction_rad)) / 1000
    return np.array([vx, vy, 0]) * scale_factor
