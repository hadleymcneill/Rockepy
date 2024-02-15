"""
This module contains the class that constructs the suborbital rocket object.
"""

import numpy as np
import math


class SuborbitalRocket:

    def __init__(self, launch_site,
                 mass_fractions,
                 structural_ratio,
                 specific_impulse,
                 diameter,
                 drag_coefficient,
                 thrust_to_weight,
                 final_coast):
        """
        Args:
            launch_site (list): Latitude and longitude of the launch site.
            mass_fractions (MassComponents): MassComponents object containing the mass fractions of the rocket.
            structural_ratio (list): List of structural ratios for each stage.
            specific_impulse (list): List of specific impulses for each stage.
            diameter (float): Diameter of the rocket (m).
            drag_coefficient (float): Drag coefficient of the rocket.
            thrust_to_weight (float): Thrust to weight ratio of the rocket.
            final_coast (float): Final coast duration of the rocket (s).
        """

        # Set the rocket input properties
        self.launch_site = launch_site
        self.position = [0, 0, 6371]
        self.velocity = [0, 0, 0.00000001]
        self.structural_ratio = np.array(structural_ratio)
        self.specific_impulses = np.array(specific_impulse)
        self.diameter = diameter
        self.drag_coefficient = drag_coefficient
        self.thrust_to_weight = thrust_to_weight
        self.final_coast = final_coast

        self.area = math.pi * self.diameter ** 2 / 4
        self.Mu = 398600.4418
        self.Y = None
        self.propagation_time = None
        self.propagation_time_step = None

        # Allocate the properties from the MassComponents instance
        self.payload_mass = mass_fractions.payload_mass
        self.mass_ratio = mass_fractions.mass_ratio
        self.step_mass = mass_fractions.step_mass
        self.empty_mass = mass_fractions.empty_mass
        self.propellant_mass = mass_fractions.propellant_mass
        self.mass = mass_fractions.total_mass
        self.mass_of_each_stage = mass_fractions.mass_of_each_stage
        self.burnout_velocity = mass_fractions.burnout_velocity
        self.effective_exhaust_velocities = mass_fractions.effective_exhaust_velocities

        self.stage_weights = 9.81 * self.mass_of_each_stage[:-1] # Weight of the stage (N)
        self.stage_thrusts = self.thrust_to_weight * self.stage_weights
        self.mass_flow_rates = self.stage_thrusts / self.effective_exhaust_velocities
        self.burnout_time = self.propellant_mass[-1] / self.mass_flow_rates[-1]
        self.parachute_deployed = False
        self.burnout = False


    def deploy_drogue_parachute(self):
        """
        Deploy the drogue parachute to slow the rocket down at apoapsis.
        """
        self.diameter = 0.25
        self.area = math.pi * self.diameter ** 2 / 4
        self.parachute_deployed = True
        self.drag_coefficient = 1.75


    def deploy_main_parachute(self):
        """
        Deploy the main parachute to slow the rocket down further when it reaches a certain altitude.
        """
        self.diameter = 1
        self.area = math.pi * self.diameter ** 2 / 4
        self.parachute_deployed = True
        self.drag_coefficient = 1.75
