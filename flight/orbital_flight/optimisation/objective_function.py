"""
This file contains the class for the objective function of the orbital trajectory optimisation problem.
"""

from flight.orbital_flight.rocket.orbital_rocket import OrbitalRocket
from flight.mass_components import MassComponents
from flight.orbital_flight.rocket.orbital_flight_thrust import OrbitalThrust
from flight.orbital_flight.orbital_flight_propagation import Propagator
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

        burnout_velocity = variables[0]
        pitch_over_angle = variables[1]


        mass_fractions = MassComponents(self.structural_ratios,
                                        self.specific_impulses,
                                        self.payload_mass,
                                        burnout_velocity)
        mass_fractions.get_mass_components()

        rocket = OrbitalRocket(self.launch_site,
                               self.target_inclination,
                               mass_fractions,
                               self.structural_ratios,
                               self.specific_impulses,
                               self.diameter,
                               self.drag_coefficient,
                               self.thrust_to_weight,
                               self.number_of_stages,
                               pitch_over_angle,
                               self.coast_duration,
                               self.final_coast)

        thrust_force = OrbitalThrust()
        trajectory = Propagator(rocket=rocket, propagation_time_step=0.01, thrust_force=thrust_force,
                                perturbations=self.perturbations)

        trajectory.propagate()
        rocket.velocity = rocket.Y[:, 3:6]
        rocket.position = rocket.Y[:, 0:3]

        velocity = rocket.velocity[-1]
        position = rocket.position[-1]

        e = ((velocity @ velocity - 398600.4418 / np.linalg.norm(position)) * position - (position @ velocity) * velocity) / 398600.4418
        eccentricity = np.linalg.norm(e)

        return mass_fractions.total_mass, eccentricity
