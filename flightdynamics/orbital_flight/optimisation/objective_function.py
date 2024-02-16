"""
This file contains the class for the objective function of the orbital ascent trajectory optimisation problem.
"""

from vehicles.orbital_rocket.orbital_rocket import OrbitalRocket
from vehicles.mass_components import MassComponents
from vehicles.orbital_rocket.orbital_flight_thrust import OrbitalThrust
from flightdynamics.orbital_flight.orbital_flight_propagation import Propagator
import numpy as np


class OptimisationFunction:
    def __init__(self, launch_site,
                 target_inclination,
                 payload_mass,
                 structural_ratios,
                 specific_impulses,
                 diameter,
                 drag_coefficient,
                 thrust_to_weight,
                 number_of_stages,
                 coast_duration,
                 final_coast,
                 perturbations=None):
        """
        Args:
            launch_site (list): The launch site of the rocket (latitude, longitude).
            target_inclination (float): The target inclination of the orbit.
            payload_mass (float): The mass of the payload.
            structural_ratios (list): The structural ratios of the rocket.
            specific_impulses (list): The specific impulses of the rocket.
            diameter (float): The diameter of the rocket.
            drag_coefficient (float): The drag coefficient of the rocket.
            thrust_to_weight (float): The thrust to weight ratio of the rocket.
            number_of_stages (int): The number of stages of the rocket.
            coast_duration (float): The coast duration of the rocket.
            final_coast (float): The final coast duration of the rocket.
            perturbations (list): The perturbations of the rocket.
        """
        self.launch_site = launch_site
        self.target_inclination = target_inclination
        self.payload_mass = payload_mass
        self.structural_ratios = structural_ratios
        self.specific_impulses = specific_impulses
        self.diameter = diameter
        self.drag_coefficient = drag_coefficient
        self.thrust_to_weight = thrust_to_weight
        self.number_of_stages = number_of_stages
        self.coast_duration = coast_duration
        self.final_coast = final_coast
        self.perturbations = perturbations if perturbations is not None else []

    def Optimisation(self, variables):
        """
        This is the objective function that optimises the fuel mass and of the rocket
        and targets a circular orbit around the Earth.
        """

        # Variables to optimise
        burnout_velocity = variables[0]
        pitch_over_angle = variables[1]

        # Structuring the problem for current optimisation variables
        mass_fractions = MassComponents(self.structural_ratios,
                                        self.specific_impulses,
                                        self.payload_mass,
                                        burnout_velocity)
        mass_fractions.get_mass_components()
        rocket = OrbitalRocket(self.launch_site,
                               self.target_inclination,
                               mass_fractions,
                               self.diameter,
                               self.drag_coefficient,
                               self.thrust_to_weight,
                               self.number_of_stages,
                               pitch_over_angle,
                               self.coast_duration,
                               self.final_coast)
        rocket.optimise_mode = True
        trajectory = Propagator(rocket=rocket,
                                propagation_time_step=0.01,
                                thrust_force=OrbitalThrust(),
                                perturbations=self.perturbations)

        # Propagate the trajectory for current optimisation variables
        trajectory.propagate()

        # Calculate the eccentricity of the orbit insertion
        rocket.velocity = rocket.Y[:, 3:6]
        rocket.position = rocket.Y[:, 0:3]
        velocity = rocket.velocity[-1]
        position = rocket.position[-1]
        e = ((velocity @ velocity - 398600.4418 / np.linalg.norm(position)) * position - (position @ velocity) * velocity) / 398600.4418
        eccentricity = np.linalg.norm(e)

        return mass_fractions.total_mass, eccentricity
