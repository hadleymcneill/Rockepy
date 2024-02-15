from flight.orbital_flight.optimisation.optimiser import OrbitalFlightOptimiser
from aerodynamics.perturbations import DragPerturbation

thrust_to_weight = 1.5
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


optimiser = OrbitalFlightOptimiser(launch_site, target_inclination, payload_mass, structural_ratios, specific_impulses, diameter, drag_coefficient, thrust_to_weight, number_of_stages, coast_duration, final_coast=5500, perturbations=perturbations)
optimiser.optimise(population_size=100, generations=1000, algorithm='ihs')
optimiser.report()
