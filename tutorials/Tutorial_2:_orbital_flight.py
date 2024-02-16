from flightdynamics.orbital_flight import *
from aerodynamics import *
from mission_analysis import *
from vehicles import *

# Introduction
# ============
# This tutorial provides a step-by-step guide on conducting an orbital launch using Rockepy.
# From setting up the orbital rocket configuration, including launch site, target orbit parameters, and rocket specifications,
# to propagating the trajectory and analysing the orbital flight profile, this guide aims to guide the process
# of achieving orbit with Rockepy. Emphasis is placed on understanding the impact of various design and environmental parameters
# on the mission's success, offering users a insights into the flight dynamics, orbital mechanics, and mission planning used for Rockepy.

# Step 1: Initial Setup
# =====================
# Establish the baseline configuration for our orbital rocket. This includes specifying the launch site (latitude, longitude),
# target inclination, structural ratios for each stage, specific impulses, payload mass, burnout velocities,
# rocket diameter, drag coefficient, thrust to weight ratio, number of stages, pitch-over angle, coast duration
# between stages, and final coast duration before payload deployment. These parameters form the core of our mission design.
rocket = OrbitalRocket(launch_site=[28, -81],  # Kennedy Space Center for this example
                       target_inclination=30,  # Target orbit inclination (deg)
                       structural_ratios=[0.15, 0.15, 0.15],  # Structural ratios for each stage
                       specific_impulses=[455, 455, 455],  # Specific impulses for each stage
                       payload_mass=10000,  # Payload mass (kg)
                       burnout_velocity=11000,  # Burnout velocity for orbit insertion (m/s)
                       diameter=5,  # Rocket diameter (m)
                       drag_coefficient=0.5,  # Drag coefficient
                       thrust_to_weight=1.3,  # Thrust to weight ratio
                       number_of_stages=3,  # Number of stages
                       pitch_over_angle=0.035,  # Pitch-over angle after launch (deg)
                       coast_duration=3,  # Coast duration between stages (s)
                       final_coast=100)  # Final coast duration before payload deployment (s)

# Step 2: Rocket Trajectory Propagation
# =====================================
# With the rocket's design finalised, we proceed to simulate its ascent through the atmosphere and into the target orbit.
# The propagation takes into account the specified design parameters, the thrust model,environmental conditions, and dynamic perturbations,
# such as atmospheric drag, to accurately model the rocket's trajectory and performance throughout the launch sequence.
# Here Low winds are applied, Refer to aerodynamics/atmospheric_model.py for more wind condition options.
trajectory = Propagator(rocket=rocket,
                        propagation_time_step=0.01,  # Time step for propagation (s)
                        thrust_force=OrbitalThrust(),  # Orbital thrust force model for staged propulsion
                        perturbations=[DragPerturbation(wind_condition="Low")])  # Atmospheric model
trajectory.propagate()

# Step 3: Orbit Insertion and Flight Profile Analysis
# ===================================================
# Analyse the flight profile of the rocket post-propagation. This step involves reporting on various flight parameters
# such as velocity, acceleration, altitude, mass, flight path angle, and dynamic pressure over time. Additionally,
# a 2D flight profile is generated to visually depict each phase of the trajectory along with an advanced 3D flight profile.
PropagationProfile(rocket).report_orbital()

# Optional: Can also retrieve specfic trajectory data with commands such as report_velocity(), report_altitude(), etc.