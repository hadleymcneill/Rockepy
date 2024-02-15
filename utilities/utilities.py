"""
This file contains utility functions for the project.
"""

import numpy as np


def set_axes_equal(ax):
    """
    Set 3D plot axes to equal scale for matplotlib.

    Args:
        ax (matplotlib.axes._subplots.Axes3DSubplot): The 3D plot axes.
    """
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    max_range = max([x_range, y_range, z_range])

    x_mid = np.mean(x_limits)
    y_mid = np.mean(y_limits)
    z_mid = np.mean(z_limits)

    ax.set_xlim(x_mid - max_range / 2, x_mid + max_range / 2)
    ax.set_ylim(y_mid - max_range / 2, y_mid + max_range / 2)
    ax.set_zlim(z_mid - max_range / 2, z_mid + max_range / 2)


def rotation_matrix_z(angle):
    """
    Returns the rotation matrix for a given angle around the z-axis.

    Args:
        angle (float): The angle of rotation (rad).

    Returns:
        np.array: The rotation matrix.
    """
    return np.array([[np.cos(angle), -np.sin(angle), 0],
                     [np.sin(angle), np.cos(angle), 0],
                     [0, 0, 1]])


def rotation_matrix_x(angle):
    """
    Returns the rotation matrix for a given angle around the x-axis.

    Args:
        angle (float): The angle of rotation (rad).

    Returns:
        np.array: The rotation matrix.
    """
    return np.array([[1, 0, 0],
                     [0, np.cos(angle), -np.sin(angle)],
                     [0, np.sin(angle), np.cos(angle)]])


def latlon_to_xyz(lat, lon, r):
    """
    Convert latitude and longitude to xyz coordinates.

    Args:
        lat (float): Latitude (rad).
        lon (float): Longitude (rad).
        r (float): Radius of the sphere.

    Returns:
        float: x coordinate.
        float: y coordinate.
        float: z coordinate.
    """
    lat = np.radians(lat)
    lon = np.radians(lon)
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon)
    z = r * np.sin(lat)
    return x, y, z


def normalise_value(value, original_min, original_max, new_min, new_max):
    """
    Normalise a single value from its original range [original_min, original_max]
    to a new range [new_min, new_max].

    Args:
        value (float): The value to be normalised.
        original_min (float): The minimum value of the original range.
        original_max (float): The maximum value of the original range.
        new_min (float): The minimum value of the new range.
        new_max (float): The maximum value of the new range.

    Returns:
        float: The normalised value.
    """
    return new_min + (value - original_min) * (new_max - new_min) / (original_max - original_min)


def bisection_solver(function, low=1e-11, high=1, tol=1e-11, max_iter=1000):
    """
    This function solves the equation f(x) = 0 using the bisection method.

    Args:
        function (function): The function to solve
        low (float): The lower bound of the initial interval
        high (float): The upper bound of the initial interval
        tol (float): The tolerance for the solution
        max_iter (int): The maximum number of iterations

    Returns:
        float: The solution to the equation f(x) = 0
    """

    # Initialise the iteration and the midpoint
    iter = 0
    mid = (low + high) / 2

    while abs(function(mid)) > tol and iter < max_iter:
        # Update the iteration and the midpoint
        iter += 1
        if function(low) * function(mid) < 0:
            high = mid
        else:
            low = mid

        # Update the midpoint
        mid = (low + high) / 2

    return mid
