from flightdynamics.orbital_flight import *
from aerodynamics import *
from mission_analysis import *
from vehicles import *


mass_components = MassComponents(structural_ratios=[0.15, 0.15, 0.15],
                                 specific_impulses=[455, 455, 455],
                                 payload_mass=10000,
                                 burnout_velocity=11000)
mass_components.get_mass_components()


rocket = OrbitalRocket(launch_site=[28, -81],  # Kennedy Space Center (latitude, longitude)
                       target_inclination=30,
                       mass_components=mass_components,
                       diameter=5,
                       drag_coefficient=0.5,
                       thrust_to_weight=1.3,
                       number_of_stages=3,
                       pitch_over_angle=0.035,
                       coast_duration=3,
                       final_coast=100)

trajectory = Propagator(rocket=rocket,
                        propagation_time_step=0.01,
                        thrust_force=OrbitalThrust(),
                        perturbations=[DragPerturbation(wind_condition="None")])

trajectory.propagate()
PropagationProfile(rocket).report_orbital()
