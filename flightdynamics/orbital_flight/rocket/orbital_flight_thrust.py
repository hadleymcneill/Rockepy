"""
This file contains the OrbitalThrust class, which represents the thrust acting on a rocket during ascent to orbit.
"""

import numpy as np
from utilities.utilities import rotation_matrix_x


class OrbitalThrust:
    """
    This class represents the thrust acting on a rocket during propagation.
    """

    def __init__(self):
        pass

    def calculate(self, Y, t, rocket):
        """
        Calculate the thrust force for given state vector Y.

        Args:
            Y (list): State vector containing position, velocity, and mass components.
            t (float): Current time.
            rocket (OrbitalRocket): OrbitalRocket object.

        Returns:
            list: Accelerations due to thrust [du_thrust, dv_thrust, dw_thrust].
        """
        x, y, z, xdot, ydot, zdot, mass = Y
        r = np.sqrt(x**2 + y**2 + z**2)
        v = np.sqrt(xdot**2 + ydot**2 + zdot**2)

        # Determine the thrust and mass flow rate
        rocket.thrust = 0
        mass_flow_rate = 0
        for i in range(rocket.number_of_stages):

            # Thrust and mass flow rate during burn
            if t < rocket.burnout_times[i]:
                rocket.thrust = rocket.stage_thrusts[rocket.current_stage]
                mass_flow_rate = rocket.mass_flow_rates[rocket.current_stage]
                break

            # Thrust and mass flow rate during coast
            elif t < rocket.burnout_times[i] + rocket.coast_duration:
                rocket.thrust = 0
                mass_flow_rate = 0
                break

        # Vertical thrust during initial ascent from the launch pad
        if r <= 6371 + 0.110 and not rocket.gravity_turn_initiated:
            du_thrust = rocket.thrust / 1000 * x / (mass * r)
            dv_thrust = rocket.thrust / 1000 * y / (mass * r)
            dw_thrust = rocket.thrust / 1000 * z / (mass * r)

        # initiate gravity turn (Pitch over manoeuvre)
        elif r <= 6371 + 0.5 and not rocket.gravity_turn_operational:
            du_thrust = rocket.thrust / 1000 * x / (mass * r)
            dv_thrust = rocket.thrust / 1000 * y / (mass * r)
            dw_thrust = rocket.thrust / 1000 * z / (mass * r)

            thrust_vector = np.array([du_thrust, dv_thrust, dw_thrust])
            rotated_thrust_vector = thrust_vector @ rotation_matrix_x(np.radians(rocket.pitch_over_angle))
            du_thrust, dv_thrust, dw_thrust = rotated_thrust_vector
            rocket.gravity_turn_initiated = True

        # Thrust during gravity turn
        else:
            du_thrust = rocket.thrust / 1000 * xdot / (mass * v)
            dv_thrust = rocket.thrust / 1000 * ydot / (mass * v)
            dw_thrust = rocket.thrust / 1000 * zdot / (mass * v)
            rocket.gravity_turn_operational = True

        dmassdt = -mass_flow_rate

        return du_thrust, dv_thrust, dw_thrust, dmassdt
