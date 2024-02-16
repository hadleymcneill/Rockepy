from flightdynamics.suborbital_flight.rocket.suborbital_rocket import SuborbitalRocket
from flightdynamics.mass_components import MassComponents
from aerodynamics.perturbations import DragPerturbation
from flightdynamics.suborbital_flight.rocket.thrust_suborbital import SuborbitalThrust
from flightdynamics.suborbital_flight.suborbital_flight_propagation import Propagator
from mission_analysis.launch_profile import PropagationProfile


mass_components = MassComponents(structural_ratios=[0.15],
                                 specific_impulses=[455],
                                 payload_mass=3,
                                 burnout_velocity=3000)
mass_components.get_mass_components()


rocket = SuborbitalRocket(launch_site=[28, -81],  # Kennedy Space Center (latitude, longitude)
                          mass_components=mass_components,
                          diameter=0.15,
                          drag_coefficient=0.5,
                          thrust_to_weight=1.3,
                          final_coast=1000)

trajectory = Propagator(rocket=rocket,
                        propagation_time_step=0.01,
                        thrust_force=SuborbitalThrust(),
                        perturbations=[DragPerturbation(wind_condition="Very Strong")])
trajectory.propagate()
PropagationProfile(rocket).report_suborbital()