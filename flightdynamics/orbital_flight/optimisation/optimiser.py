"""
This file contains the class for the orbital flight optimiser powered with the PyGMO library.
"""

from vehicles.orbital_rocket.orbital_rocket import OrbitalRocket
from vehicles.mass_components import MassComponents
from vehicles.orbital_rocket.orbital_flight_thrust import OrbitalThrust
from flightdynamics.orbital_flight.orbital_flight_propagation import Propagator
from mission_analysis.launch_profile import PropagationProfile
import pygmo as pg
from flightdynamics.orbital_flight.optimisation.objective_function import OptimisationFunction
import time



class OrbitalFlightOptimiser:
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

    def optimise(self, population_size=100, generations=1000, algorithm='ihs'):
        """
        This method optimises the rocket for the given parameters and perturbations.

        Args:
            population_size (int): The population size of the optimisation algorithm.
            generations (int): The number of generations of the optimisation algorithm.
            algorithm (str): The optimisation algorithm to use, see the PyGMO documentation for more options.
        """

        lb, ub = self.getAlphaBounds()
        problem = MyProblem(lb, ub,
                            self.launch_site,
                            self.target_inclination,
                            self.payload_mass,
                            self.structural_ratios,
                            self.specific_impulses,
                            self.diameter,
                            self.drag_coefficient,
                            self.thrust_to_weight,
                            self.number_of_stages,
                            self.coast_duration,
                            10,  # Unnecessary to simulate full final coast duration during optimisation
                            self.perturbations)


        # Build the problem, algorithm, and parameters
        prob = pg.problem(problem)
        pop = pg.population(prob, size=population_size)
        algo = pg.algorithm(eval(f"pg.{algorithm}(gen=generations)"))

        # Report optimisation progress every 25 generations
        algo.set_verbosity(25)

        # Evolve the population (Optimise)
        start_time = time.perf_counter()
        pop = algo.evolve(pop)
        print(f"Simulation Time: {time.perf_counter() - start_time} Seconds")

        # Retrieve the best solution
        X = pop.champion_x
        self.burnout_velocity = X[0]
        self.pitch_over_angle = X[1]


    def report(self):
        """
        This method reports the best solution found by the optimisation algorithm.
        """

        # Build the rocket for the best optimisation variables
        rocket = OrbitalRocket(self.launch_site,
                               self.target_inclination,
                               self.structural_ratios,
                               self.specific_impulses,
                               self.payload_mass,
                               self.burnout_velocity,
                               self.diameter,
                               self.drag_coefficient,
                               self.thrust_to_weight,
                               self.number_of_stages,
                               self.pitch_over_angle,
                               coast_duration=self.coast_duration,
                               final_coast=self.final_coast)

        # Propagate the trajectory and report the results
        trajectory = Propagator(rocket=rocket,
                                propagation_time_step=0.01,
                                thrust_force=OrbitalThrust(),
                                perturbations=self.perturbations)
        trajectory.propagate()
        PropagationProfile(rocket).report_orbital()

    def getAlphaBounds(self, target_burnout_velocity_low=6000, target_burnout_velocity_high=12000,
                       pitch_over_angle_low=0.001, pitch_over_angle_high=0.5):
        """
        This method returns the bounds of the optimisation problem already set for the targeting stable orbit.
        """
        lb = [target_burnout_velocity_low] + [pitch_over_angle_low]
        ub = [target_burnout_velocity_high] + [pitch_over_angle_high]
        return lb, ub


class MyProblem:
    """
    This class contains the problem definition of the orbital flight optimisation problem built with the PyGMO library.
    """
    def __init__(self, lb, ub,
                 launch_site,
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

        self.lb = lb
        self.ub = ub

        self.problemFunction = OptimisationFunction(launch_site,
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
                                                    perturbations)
    def fitness(self, variables):
        mass, eccentricity = self.problemFunction.Optimisation(variables)
        eccentricity_constraint = abs(eccentricity)
        return [mass] + [eccentricity_constraint]

    def get_bounds(self):
        return (self.lb, self.ub)

    def get_nobj(self):
        return 1

    def get_nec(self):
        return 0

    def get_nic(self):
        return 1

    def name(self):
        return f"rocket"