from flightdynamics.suborbital_flight import *
from aerodynamics import *
from mission_analysis import *
from vehicles import *

# Introduction
# ============
# This tutorial is designed to guide users through the planning and execution of a suborbital flight mission using Rockepy.
# It will cover the construction of a rocket model, the propagation of its trajectory under various conditions, and the analysis
# of its flight profile. This guide aims to familiarise users with Rockepy's capabilities for suborbital mission planning and execution,
# emphasising key aspects such as rocket build, aerodynamic considerations, and the impact of environmental perturbations.

# Step 1: Initial Setup
# =====================
# Define the launch site and rocket parameters. These include the launch site coordinates (latitude and longitude),
# structural ratios, specific impulses, payload mass, burnout velocity, diameter, drag coefficient, thrust to weight ratio,
# and the final coast duration. This setup will constitute the baseline configuration of our rocket for the mission.
rocket = SuborbitalRocket(launch_site=[28, -81],  # Kennedy Space Center for this example.
                          structural_ratios=[0.15],  # Structural ratio
                          specific_impulses=[455],  # Specific impulse
                          payload_mass=3,  # Payload mass (kg)
                          burnout_velocity=3000,  # Burnout velocity (m/s)
                          diameter=0.15,  # Diameter (m)
                          drag_coefficient=0.5,  # Drag coefficient
                          thrust_to_weight=1.3,  # Thrust to weight ratio
                          final_coast=1000)  # Final coast duration (s) - Unless the rocket lands

# Step 2: Rocket Trajectory Propagation
# =====================================
# Propagate the trajectory considering the defined launch parameters and thrust model along with environmental conditions.
# The trajectory is propagated  phase by phase (Ascent, Coast to apoapsis, drogue parachute, and main parachute),
# with a high-resolution time step to accurately simulate the flight dynamics. Additionally, drag perturbation with
# variable wind conditions is applied to assess its impact on the trajectory. Refer to aerodynamics/atmospheric_model.py
# for more wind condition options.
trajectory = Propagator(rocket=rocket,
                        propagation_time_step=0.01,  # Time step for propagation (s)
                        thrust_force=SuborbitalThrust(),  # Thrust force model
                        perturbations=[DragPerturbation(wind_condition="Very Strong")]) # Atmospheric model
trajectory.propagate()

# Step 3: Flight Profile Analysis
# ===============================
# Analyse the flight profile of the rocket post-propagation. This step involves reporting on various flight parameters
# such as velocity, acceleration, altitude, mass, flight path angle, and dynamic pressure over time. Additionally,
# a 3D flight profile is generated to visually depict each phase of the trajectory.
PropagationProfile(rocket).report_suborbital()

# Optional: Can also retrieve specfic trajectory data with commands such as report_velocity(), report_altitude(), etc.
