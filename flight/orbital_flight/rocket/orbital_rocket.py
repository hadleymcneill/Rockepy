"""
This module contains the class that constructs the orbital rocket object.
"""

import numpy as np
import math


class OrbitalRocket:

    def __init__(self, launch_site,
                 target_inclination,
                 mass_fractions,
                 structural_ratios,
                 specific_impulses,
                 diameter,
                 drag_coefficient,
                 thrust_to_weight,
                 number_of_stages,
                 pitch_over_angle,
                 coast_duration,
                 final_coast):
        """
        Args:
            launch_site (list): Latitude and longitude of the launch site.
            target_inclination (float): The inclination of the target orbit (deg).
            mass_fractions (MassComponents): MassComponents object containing the mass fractions of the rocket.
            structural_ratios (list): List of structural ratios for each stage.
            specific_impulses (list): List of specific impulses for each stage.
            diameter (float): Diameter of the rocket (m).
            drag_coefficient (float): Drag coefficient of the rocket.
            thrust_to_weight (float): Thrust to weight ratio of the rocket.
            number_of_stages (int): Number of stages of the rocket.
            pitch_over_angle (float): Pitch over angle of the rocket for the gravity turn (deg).
        """

        # Set the rocket input properties
        self.launch_site = launch_site
        self.target_inclination = target_inclination
        self.position = [0, 0, 6371]
        self.velocity = [0, 0, 0.00000001]
        self.structural_ratios = np.array(structural_ratios)
        self.specific_impulses = np.array(specific_impulses)
        self.diameter = diameter
        self.drag_coefficient = drag_coefficient
        self.thrust_to_weight = thrust_to_weight
        self.number_of_stages = number_of_stages
        self.pitch_over_angle = pitch_over_angle
        self.coast_duration = coast_duration
        self.final_coast = final_coast

        self.area = math.pi * self.diameter ** 2 / 4
        self.Mu = 398600.4418
        self.Y = None
        self.propagation_time = None
        self.propagation_time_step = None
        self.optimise_mode = False

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

        self.stage_weights = 9.81 * self.mass_of_each_stage[:-1]
        self.stage_thrusts = self.thrust_to_weight * self.stage_weights
        self.mass_flow_rates = self.stage_thrusts / self.effective_exhaust_velocities

        # Determine the burnout times for each stage
        self.burnout_times = []
        for i in range(self.number_of_stages):
            if i == 0:
                self.burnout_times.append(self.propellant_mass[i] / self.mass_flow_rates[i])
            elif i < self.number_of_stages - 1:
                burn_duration = self.propellant_mass[i] / self.mass_flow_rates[i]
                self.burnout_times.append(self.burnout_times[i - 1] + self.coast_duration + burn_duration)
            else:
                burn_duration = self.propellant_mass[i] / self.mass_flow_rates[i]
                self.burnout_times.append(self.burnout_times[i - 1] + burn_duration)

        if self.target_inclination < self.launch_site[0]:
            raise ValueError("The target inclination must be greater than the latitude of the launch site")
