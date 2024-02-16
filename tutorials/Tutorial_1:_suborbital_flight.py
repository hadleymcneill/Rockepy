from flightdynamics.suborbital_flight import *
from aerodynamics import *
from mission_analysis import *
from vehicles import *


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