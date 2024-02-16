from flight.orbital_flight.rocket.orbital_rocket import OrbitalRocket
from flight.mass_components import MassComponents
from flight.orbital_flight.rocket.orbital_flight_thrust import OrbitalThrust
from flight.orbital_flight.orbital_flight_propagation import Propagator
from mission_analysis.launch_profile import PropagationProfile
import pygmo as pg
from flight.orbital_flight.optimisation.objective_function import OptimisationFunction
import time


class MyProblem:

    def __init__(self, lb, ub,
       launch_site, target_inclination, payload_mass, structural_ratios, specific_impulses, diameter, drag_coefficient, thrust_to_weight, number_of_stages, coast_duration, final_coast, perturbations=None):

        self.lb = lb
        self.ub = ub

        self.problemFunction = OptimisationFunction(launch_site, target_inclination, payload_mass, structural_ratios, specific_impulses, diameter, drag_coefficient, thrust_to_weight, number_of_stages, coast_duration, final_coast, perturbations)

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

class OrbitalFlightOptimiser:
    def __init__(self, launch_site, target_inclination, payload_mass, structural_ratios, specific_impulses, diameter, drag_coefficient, thrust_to_weight, number_of_stages, coast_duration, final_coast, perturbations=None):
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
                            self.final_coast,
                            self.perturbations)


        # Create an instance of your problem
        prob = pg.problem(problem)

        # Create a population
        pop = pg.population(prob, size=population_size)

        # Select an algorithm
        algo = pg.algorithm(eval(f"pg.{algorithm}(gen=generations)"))

        algo.set_verbosity(25)

        start_time = time.perf_counter()

        # Evolve the population
        pop = algo.evolve(pop)

        elapsed_time = time.perf_counter() - start_time

        print(f"Simulation Time: {elapsed_time} Seconds")

        X = pop.champion_x

        self.burnout_velocity = X[0]
        self.pitch_over_angle = X[1]


    def report(self):
        mass_components = MassComponents(self.structural_ratios, self.specific_impulses, self.payload_mass, self.burnout_velocity)
        mass_components.get_mass_components()

        rocket = OrbitalRocket(self.launch_site, self.target_inclination, mass_components,
                               self.diameter, self.drag_coefficient,
                               self.thrust_to_weight, self.number_of_stages, self.pitch_over_angle, coast_duration=self.coast_duration,
                               final_coast=self.final_coast)

        thrust_force = OrbitalThrust()
        trajectory = Propagator(rocket=rocket, propagation_time_step=0.01, thrust_force=thrust_force,
                                perturbations=self.perturbations)

        trajectory.propagate()
        PropagationProfile(rocket).report_orbital()

    def getAlphaBounds(self, target_burnout_velocity_low=6000, target_burnout_velocity_high=12000,
                       pitch_over_angle_low=0.001, pitch_over_angle_high=0.5):
        lb = [target_burnout_velocity_low] + [pitch_over_angle_low]
        ub = [target_burnout_velocity_high] + [pitch_over_angle_high]
        return lb, ub