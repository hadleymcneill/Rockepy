from flight.orbital_flight.rocket.orbital_rocket import OrbitalRocket
from flight.mass_components import MassComponents
from aerodynamics.perturbations import DragPerturbation
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


def getAlphaBounds(lagrange_multiplier_low, lagrange_multiplier_high,
                   pitch_over_angle_low=0.001, pitch_over_angle_high=0.5):

    lb = [lagrange_multiplier_low] + [pitch_over_angle_low]

    ub = [lagrange_multiplier_high] + [pitch_over_angle_high]

    return lb, ub


thrust_to_weight = 1.5  # OrbitalThrust to weight ratio
payload_mass = 10000 # Payload mass (kg) fuel + rocket
drag_coefficient = 0.5

number_of_stages = 3
structural_ratios = [0.15] * number_of_stages
specific_impulses = [455] * number_of_stages
coast_duration = 3
diameter = 5
launch_site = [28, -81]
target_inclination = 30
perturbations = [DragPerturbation()]

lb, ub = getAlphaBounds(6000, 12000)

problem = MyProblem(lb, ub,
                    launch_site,
                    target_inclination,
                    payload_mass,
                    structural_ratios,
                    specific_impulses,
                    diameter,
                    drag_coefficient,
                    thrust_to_weight,
                    number_of_stages,
                    coast_duration=coast_duration,
                    final_coast=10,
                    perturbations=perturbations)


algorithm = 'ihs'
population_size = 100
generations = 1000

# Create an instance of your problem
prob = pg.problem(problem)

# Create a population
pop = pg.population(prob, size=population_size)

# Select an algorithm
algo = pg.algorithm(eval(f"pg.{algorithm}(gen=generations)"))

algo.set_verbosity(1)

start_time = time.perf_counter()

# Evolve the population
pop = algo.evolve(pop)

elapsed_time = time.perf_counter() - start_time

print(f"Elapsed time: {elapsed_time} seconds")

X = pop.champion_x
F = pop.champion_f

print(f"X: {X}")
print(f"F: {F}")

burnout_velocity = X[0]
pitch_over_angle = X[1]

mass_fractions = MassComponents(structural_ratios, specific_impulses, payload_mass, burnout_velocity)
mass_fractions.get_mass_components()

rocket = OrbitalRocket(launch_site, target_inclination, mass_fractions, structural_ratios, specific_impulses,
                       diameter, drag_coefficient,
                       thrust_to_weight, number_of_stages, pitch_over_angle, coast_duration=coast_duration,
                       final_coast=100)

thrust_force = OrbitalThrust()

trajectory = Propagator(rocket=rocket, propagation_time_step=0.01, thrust_force=thrust_force,
                        perturbations=perturbations)

trajectory.propagate()
PropagationProfile(rocket).propagation_profile_orbital_true_view()
