"""
This file contains the SuborbitalThrust class, which represents the thrust acting on a rocket during suborbital ascent.
"""

import numpy as np


class SuborbitalThrust:
    """
    This class represents the thrust acting on a rocket during propagation.
    """
    def __init__(self):
        pass

    def calculate(self, Y, t, rocket):
        """
        Calculate the drag force perturbation for given state vector Y.

        Args:
            Y (list): State vector containing position and velocity components.
            t (float): Current time (unused in this function but needed for consistency).
            rocket (OrbitalRocket): OrbitalRocket object.

        Returns:
            list: Accelerations due to thrust [du_thrust, dv_thrust, dw_thrust].
        """
        x, y, z, xdot, ydot, zdot, mass = Y
        r = np.sqrt(x**2 + y**2 + z**2)

        # Thrust and mass flow rate during burn
        if not rocket.burnout:
            rocket.thrust = rocket.stage_thrusts[0]
            rocket.mass_flow_rate = rocket.mass_flow_rates[0]

        # Thrust and mass flow rate during coast
        else:
            rocket.thrust = 0
            rocket.mass_flow_rate = 0

        # Thrust always acts vertically during ascent
        du_thrust = (rocket.thrust * x / (mass * r)) / 1000
        dv_thrust = (rocket.thrust * y / (mass * r)) / 1000
        dw_thrust = (rocket.thrust * z / (mass * r)) / 1000

        dmassdt = -rocket.mass_flow_rate

        return du_thrust, dv_thrust, dw_thrust, dmassdt
