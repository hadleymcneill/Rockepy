from flight.orbital_flight.rocket.orbital_rocket import OrbitalRocket
from flight.mass_components import MassComponents
from aerodynamics.perturbations import DragPerturbation
from flight.orbital_flight.rocket.orbital_flight_thrust import OrbitalThrust
from flight.orbital_flight.orbital_flight_propagation import Propagator
from mission_analysis.launch_profile import PropagationProfile


thrust_to_weight = 1.3
burnout_velocity = 11000  # Burnout velocity target (m/s) - not accounting for losses
payload_mass = 10000  # Payload mass (kg)

number_of_stages = 3
structural_ratios = [0.15] * number_of_stages
specific_impulses = [455] * number_of_stages

diameter = 5
drag_coefficient = 0.5
pitch_over_angle = 0.035
coast_duration = 3

mass_fractions = MassComponents(structural_ratios, specific_impulses, payload_mass, burnout_velocity)
mass_fractions.get_mass_components()

perturbations = [DragPerturbation()]

launch_site = [28, -81]
target_inclination = 30

rocket = OrbitalRocket(launch_site, target_inclination, mass_fractions, structural_ratios, specific_impulses,
                       diameter, drag_coefficient,
                       thrust_to_weight, number_of_stages, pitch_over_angle, coast_duration=coast_duration,
                       final_coast=100)

thrust_force = OrbitalThrust()
trajectory = Propagator(rocket=rocket, propagation_time_step=0.01, thrust_force=thrust_force,
                        perturbations=perturbations)

trajectory.propagate()

PropagationProfile(rocket).report_orbital()
