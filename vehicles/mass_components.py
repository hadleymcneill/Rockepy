"""
This file contains the class for calculating the mass components of a rocket.
"""

from utilities.utilities import bisection_solver
import numpy as np


class MassComponents:
    def __init__(self, structural_ratios, specific_impulses, payload_mass, burnout_velocity):
        """
        Args:
            structural_ratios (list): List of structural ratios for each stage.
            specific_impulses (list): List of specific impulses for each stage.
            payload_mass (float): Mass of the payload (kg).
            burnout_velocity (float): Burnout velocity of the rocket (m/s).
        """
        self.structural_ratios = np.array(structural_ratios)
        self.specific_impulses = np.array(specific_impulses)
        self.payload_mass = payload_mass
        self.burnout_velocity = burnout_velocity

        self.effective_exhaust_velocities = self.specific_impulses * 9.81

    def get_mass_components(self):
        """
        This method calculates the mass components of the rocket.
        """

        # The optimum staging function to be solved to find the optimum mass ratio for each stage
        def optimum_staging_function(L): return (np.sum(self.effective_exhaust_velocities *
                                                 np.log(self.effective_exhaust_velocities * L - 1)) -
                                                 np.log(L) * np.sum(self.effective_exhaust_velocities) -
                                                 np.sum(self.effective_exhaust_velocities *
                                                 np.log(self.effective_exhaust_velocities * self.structural_ratios)) -
                                                 self.burnout_velocity)

        # Solve the optimum staging function using the bisection method
        lagrange_multiplier = bisection_solver(optimum_staging_function,
                                               1 / np.min(self.effective_exhaust_velocities) + 1e-11,
                                               np.min(self.effective_exhaust_velocities * (1 - self.structural_ratios)))

        # Calculate the mass ratio for each stage
        self.mass_ratio = (self.effective_exhaust_velocities * lagrange_multiplier - 1) / (
                    self.effective_exhaust_velocities * self.structural_ratios * lagrange_multiplier)

        # Calculate the resulting mass components for each stage
        step_mass = [self.payload_mass]
        for i in range(len(self.mass_ratio), 0, -1):
            step_mass.append(
                (self.mass_ratio[i - 1] - 1) / (1 - self.mass_ratio[i - 1] * self.structural_ratios[i - 1]) * np.sum(
                    step_mass))

        self.step_mass = np.flip(step_mass)
        self.empty_mass = self.step_mass[0:-1] * self.structural_ratios
        self.propellant_mass = self.step_mass[0:-1] - self.empty_mass
        self.total_mass = np.sum(self.step_mass)

        # Calculate the mass of each stage
        mass_of_each_stage = []
        for i in range(len(self.step_mass)):
            mass_of_each_stage.append(np.sum(self.step_mass[i:]))

        self.mass_of_each_stage = np.array(mass_of_each_stage)
