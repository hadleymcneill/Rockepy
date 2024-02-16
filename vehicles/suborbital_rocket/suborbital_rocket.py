"""
This module contains the class that constructs the suborbital rocket object.
"""

from vehicles.mass_components import MassComponents
import math


class SuborbitalRocket:

    def __init__(self, launch_site,
                 structural_ratios,
                 specific_impulses,
                 payload_mass,
                 burnout_velocity,
                 diameter,
                 drag_coefficient,
                 thrust_to_weight,
                 final_coast):
        """
        Args:
            launch_site (list): Latitude and longitude of the launch site.
            structural_ratios (list): List of structural ratios for each stage.
            specific_impulses (list): List of specific impulses for each stage.
            payload_mass (float): Mass of the payload (kg).
            burnout_velocity (float): Burnout velocity of the rocket (m/s).
            diameter (float): Diameter of the rocket (m).
            drag_coefficient (float): Drag coefficient of the rocket.
            thrust_to_weight (float): Thrust to weight ratio of the rocket.
            final_coast (float): Final coast duration of the rocket (s).
        """

        # Set the rocket input properties
        self.launch_site = launch_site
        self.position = [0, 0, 6371]
        self.velocity = [0, 0, 0.00000001]
        self.diameter = diameter
        self.drag_coefficient = drag_coefficient
        self.thrust_to_weight = thrust_to_weight
        self.final_coast = final_coast

        self.area = math.pi * self.diameter ** 2 / 4
        self.Mu = 398600.4418
        self.Y = None
        self.propagation_time = None
        self.propagation_time_step = None

        # Retrieve and allocate the properties of the mass components
        mass_components = MassComponents(structural_ratios=structural_ratios,
                                         specific_impulses=specific_impulses,
                                         payload_mass=payload_mass,
                                         burnout_velocity=burnout_velocity)
        mass_components.get_mass_components()
        self.payload_mass = mass_components.payload_mass
        self.mass_ratio = mass_components.mass_ratio
        self.step_mass = mass_components.step_mass
        self.empty_mass = mass_components.empty_mass
        self.propellant_mass = mass_components.propellant_mass
        self.mass = mass_components.total_mass
        self.mass_of_each_stage = mass_components.mass_of_each_stage
        self.burnout_velocity = mass_components.burnout_velocity
        self.structural_ratios = mass_components.structural_ratios
        self.specific_impulses = mass_components.specific_impulses
        self.effective_exhaust_velocities = mass_components.effective_exhaust_velocities

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
