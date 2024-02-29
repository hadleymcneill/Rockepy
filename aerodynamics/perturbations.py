"""
This file contains the classes that define the perturbations acting on a missile during flight.
"""

from aerodynamics.atmospheric_model import atmospheric_density, wind_model
import numpy as np


class DragPerturbation:
    """
    This class represents the drag acting on a missile during propagation.
    """
    def __init__(self, wind_condition="None"):
        """
        Args:
            wind_condition (str): Wind condition ("None", "Light", "Moderate", "Strong", "Very Strong").
        """
        self.wind_condition = wind_condition

    def calculate(self, Y, t, rocket):
        """
        Calculate the drag force perturbation for given state vector Y.

        Args:
            Y (list): State vector containing position, velocity and mass components.
            t (float): Current time (unused in this function but needed for consistency).
            rocket (OrbitalRocket): OrbitalRocket object.

        Returns:
            list: Perturbation accelerations due to drag [du_drag, dv_drag, dw_drag].
        """

        # Calculate atmospheric density and velocity relative to the rotating atmosphere and wind.
        x, y, z, xdot, ydot, zdot, mass = Y
        r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        density = atmospheric_density(r - 6371)
        central_body_angular_velocity = np.array([0, 0, 7.2921159e-5])
        rocket_velocity = np.array([xdot, ydot, zdot])

        if self.wind_condition != "None":
            wind_velocity = wind_model(r - 6371, self.wind_condition)
        else:
            wind_velocity = np.array([0, 0, 0])

        velocity_relative_to_atmosphere = rocket_velocity - wind_velocity - np.cross(central_body_angular_velocity,
                                                                                     [x, y, z])
        vrel_magnitude = np.linalg.norm(velocity_relative_to_atmosphere)

        # Calculate the drag force perturbation acceleration
        du_drag = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * rocket.drag_coefficient * rocket.area / mass *
                   velocity_relative_to_atmosphere[0] / vrel_magnitude) / 1000
        dv_drag = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * rocket.drag_coefficient * rocket.area / mass *
                   velocity_relative_to_atmosphere[1] / vrel_magnitude) / 1000
        dw_drag = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * rocket.drag_coefficient * rocket.area / mass *
                   velocity_relative_to_atmosphere[2] / vrel_magnitude) / 1000
        return du_drag, dv_drag, dw_drag


class Lift:
    """
    This class represents the lift acting on a missile during propagation.
    """

    def __init__(self, Cl):
        """
        Args:
            Cl (float): Lift coefficient.
        """
        self.Cl = Cl

    def calculate(self, Y, t, rocket):
        """
        Calculate the lift force perturbation for given state vector Y.

        Args:
            Y (list): State vector containing position, velocity and mass components.
            t (float): Current time (unused in this function but needed for consistency).
            rocket (OrbitalRocket): OrbitalRocket object.

        Returns:
            list: Accelerations due to lift [du_lift, dv_lift, dw_lift].
        """

        # Calculate the atmospheric density and relative velocity
        x, y, z, xdot, ydot, zdot, mass = Y
        central_body_angular_velocity = [0, 0, 7.2921159e-5]
        velocity_relative_to_atmosphere = [xdot, ydot, zdot] - np.cross(central_body_angular_velocity,
                                                                        [xdot, ydot, zdot])
        vrel_magnitude = np.linalg.norm(velocity_relative_to_atmosphere)
        density = atmospheric_density(np.linalg.norm([x, y, z]) - 6371)

        # Calculate normal vector to the plane of motion (perpendicular to velocity vector)
        position_vector = np.array([x, y, z])
        normal_vector = np.cross(velocity_relative_to_atmosphere, position_vector)
        lift_direction = np.cross(normal_vector, velocity_relative_to_atmosphere)
        lift_direction_normalized = -lift_direction / np.linalg.norm(lift_direction)

        # Calculate the lift force perturbation acceleration
        du_lift = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * self.Cl * rocket.area / mass *
                   lift_direction_normalized[0]) / 1000
        dv_lift = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * self.Cl * rocket.area / mass *
                   lift_direction_normalized[1]) / 1000
        dw_lift = (- 0.5 * density * (vrel_magnitude * 1000) ** 2 * self.Cl * rocket.area / mass *
                   lift_direction_normalized[2]) / 1000
        return du_lift, dv_lift, dw_lift
