from flightdynamics.orbital_flight import *
from aerodynamics import *



optimiser = OrbitalFlightOptimiser(launch_site=[28, -81], # Kennedy Space Center
                                   target_inclination=30,
                                   payload_mass=10000,
                                   structural_ratios=[0.15, 0.15, 0.15],
                                   specific_impulses=[455, 455, 455],
                                   diameter=5,
                                   drag_coefficient=0.5,
                                   thrust_to_weight=1.5,
                                   number_of_stages=3,
                                   coast_duration=3,
                                   final_coast=5500,
                                   perturbations=[DragPerturbation(wind_condition="None")])

optimiser.optimise(population_size=100, generations=1000, algorithm='ihs')
optimiser.report()
