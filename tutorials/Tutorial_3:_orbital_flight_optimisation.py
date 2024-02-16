from flightdynamics.orbital_flight import *
from aerodynamics import *

# Introduction
# ============
# This tutorial is dedicated to showcasing the process of optimising an orbital flight mission using Rockepy.
# It focuses on fine-tuning various mission parameters such as the targeted burnout velocity and the pitch-over angle
# to achieve an optimal flight profile with a minimised mass and a stable circular orbit insertion for the payload.
# The tutorial guides users through defining the optimisation problem, selecting the optimisation algorithm,
# running the optimisation process, and interpreting the results. This step-by-step guide aims to demonstrate the
# powerful capabilities of Rockepy in enhancing mission efficiency and performance through optimisation.

# Step 1: Optimisation Setup
# ==========================
# Begin by specifying the initial conditions and constraints for the orbital flight optimisation problem.
# This includes the launch site, target orbit inclination, payload mass, structural ratios, specific impulses,
# rocket diameter, drag coefficient, thrust to weight ratio, number of stages, coast durations,
# and the environmental perturbations to consider. These parameters form the basis of our optimisation problem.
# Here no wind is applied, Refer to aerodynamics/atmospheric_model.py for more wind condition options.
optimiser = OrbitalFlightOptimiser(launch_site=[28, -81],  # Kennedy Space Center
                                   target_inclination=30,  # Target orbit inclination (deg)
                                   payload_mass=10000,  # Payload mass (kg)
                                   structural_ratios=[0.15, 0.15, 0.15],  # Initial structural ratios
                                   specific_impulses=[455, 455, 455],  # Initial specific impulses
                                   diameter=5,  # Rocket diameter (m)
                                   drag_coefficient=0.5,  # Drag coefficient
                                   thrust_to_weight=1.5,  # Thrust to weight ratio
                                   number_of_stages=3,  # Number of stages
                                   coast_duration=3,  # Coast duration between stages (s)
                                   final_coast=10,  # Final coast duration before payload deployment (s)
                                   perturbations=[DragPerturbation(wind_condition="None")])  # Atmospheric model

# Step 2: Running the Optimisation
# ================================
# Execute the optimisation process using the specified algorithm and parameters. The optimiser will explore
# the parameter space to find an optimal set of mission design variables that minimise the total rocket mass
# and target a circular stable orbit. The process iterates over a number of generations with a
# population sise that influences the diversity and convergence of the optimisation.
optimiser.optimise(population_size=100,  # Size of the population in each generation
                   generations=1000,  # Number of generations to evolve the solution
                   algorithm='ihs')  # Optimisation algorithm (e.g., Improved Harmony Search), see PyGMO documentation for more options

# Step 3: Optimisation Results and Analysis
# =========================================
# Upon completion of the optimisation process, generate a report that details the findings.
# This report includes results of various flight parameters such as velocity, acceleration, altitude, mass,
# flight path angle, and dynamic pressure over time. Additionally, a 2D flight profile is generated to visually
# depict each phase of the trajectory along with an advanced 3D flight profile.
optimiser.report()
