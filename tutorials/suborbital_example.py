from flight.suborbital_flight.rocket.suborbital_rocket import SuborbitalRocket
from flight.mass_components import MassComponents
from aerodynamics.perturbations import DragPerturbation
from flight.suborbital_flight.rocket.thrust_suborbital import SuborbitalThrust
from flight.suborbital_flight.suborbital_flight_propagation import Propagator
from mission_analysis.launch_profile import PropagationProfile


thrust_to_weight = 1.3  #
burnout_velocity = 3000  # Burnout velocity target (m/s) - not accounting for losses
payload_mass = 3  # Payload mass (kg)

structural_ratios = [0.15]
specific_impulses = [455]
drag_coefficient = 0.5

diameter = .15

mass_fractions = MassComponents(structural_ratios, specific_impulses, payload_mass, burnout_velocity)
mass_fractions.get_mass_components()
thrust_force = SuborbitalThrust()
perturbations = [DragPerturbation(wind_condition="Very Strong")]


launch_site = [28, -81]


rocket = SuborbitalRocket(launch_site, mass_fractions, structural_ratios, specific_impulses, diameter, drag_coefficient, thrust_to_weight, final_coast=1000)

trajectory = Propagator(rocket=rocket, propagation_time_step=0.01, thrust_force=thrust_force, perturbations=perturbations)
trajectory.propagate()

PropagationProfile(rocket).report_suborbital()