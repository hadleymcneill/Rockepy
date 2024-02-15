"""
This module contains the class for propagating the rocket trajectory of the suborbital ascent.
"""

import numpy as np
from scipy.integrate import solve_ivp


class Propagator:

    def __init__(self, rocket, propagation_time_step, thrust_force, perturbations=None):
        """
        Args:
            rocket (OrbitalRocket): OrbitalRocket object.
            propagation_time_step (float): Time step of the propagation.
            thrust_force (OrbitalThrust): OrbitalThrust object defining the thrust force acting on the rocket.
            perturbations (list): List of perturbations to be considered in the PropagationProfile.
        """
        self.rocket = rocket
        self.rocket.propagation_time_step = propagation_time_step
        self.thrust_force = thrust_force
        self.perturbations = perturbations if perturbations is not None else []

        self.body_radius = 6371

    def propagate(self):
        """
        Propagates the rocket's trajectory considering the provided perturbations.
        """

        # Initialise the state vector, state matrix combining all phases, and the time vector.
        U0 = np.concatenate((self.rocket.position, self.rocket.velocity, [self.rocket.mass]))
        combined_Y = np.array([]).reshape(0, U0.shape[0])
        combined_t_eval = np.array([])  # Initialize empty array for concatenated time evaluations

        # Initialise variables for section indices used to split the trajectory into sections for each stage.
        section_indices = []
        start_index = 0

        # Define the events for the rocket trajectory phases
        events = [[self.ground_impact_event],
                  [self.ground_impact_event, self.apoapsis_parachute_event],
                  [self.ground_impact_event, self.main_parachute_event],
                  [self.ground_impact_event]]

        # Propagate the trajectory for each phase
        t_starts = [0]
        for i in range(len(events)):

            # Determine the end time for each phase, though events will terminate the simulation early
            t_end = self.rocket.burnout_time if i == 0 else self.rocket.burnout_time + self.rocket.final_coast
            t_starts.append(sol.t[-1]) if i > 0 else None

            # Special events for each phase
            if i == 1:
                self.rocket.burnout = True
            elif i == 2:
                self.rocket.deploy_drogue_parachute()
                print(
                    f"Rocket has deployed drogue parachute at {np.linalg.norm(U0[:3]) - 6371} km altitude. t = {t_starts[i]} s.")
                self.apoapsis = np.linalg.norm(U0[:3])
            elif i == 3:
                self.rocket.deploy_main_parachute()
                print(
                    f"Rocket has deployed main parachute at {np.linalg.norm(U0[:3]) - 6371} km altitude. t = {t_starts[i]} s.")

            t_eval = np.arange(t_starts[i], t_end, self.rocket.propagation_time_step)
            sol = solve_ivp(self._state_derivatives, (t_starts[i], t_end), U0, method='RK45', t_eval=t_eval,
                            events=events[i])
            Y_sol = sol.y.T
            combined_Y = np.concatenate((combined_Y, Y_sol), axis=0)

            # Readjust the time evaluation array to match the length of the solution
            t_eval = np.arange(t_starts[i], round(sol.t[-1], 2) + self.rocket.propagation_time_step,
                               self.rocket.propagation_time_step)
            readjustment_error = abs(len(t_eval) - len(Y_sol))
            combined_t_eval_i = np.concatenate((combined_t_eval, t_eval))
            combined_t_eval = combined_t_eval_i[:-readjustment_error] if readjustment_error > 0 else combined_t_eval_i

            # Update section indices
            end_index = start_index + len(t_eval)
            section_indices.append((start_index, end_index))
            start_index = end_index

            # Update initial state of the next phase to the final state from the current phase
            U0 = sol.y[:, -1]

        self.rocket.Y = combined_Y
        self.rocket.t_eval = combined_t_eval
        self.rocket.section_indices = section_indices

        return self.rocket.Y

    def _state_derivatives(self, t, Y):
        """
        Calculate the state derivatives for the propagation.

        Args:
            Y (list): State vector containing position, velocity, and mass components.
            t (float): Current time.

        Returns:
            list: State derivatives [dxdt, dydt, dzdt, dudt, dvdt, dwdt, dmassdt].
        """
        x, y, z, xdot, ydot, zdot, mass = Y
        r = np.sqrt(x ** 2 + y ** 2 + z ** 2)

        # Calculate the state derivatives
        dxdt = xdot
        dydt = ydot
        dzdt = zdot
        dudt = -self.rocket.Mu * x / r ** 3
        dvdt = -self.rocket.Mu * y / r ** 3
        dwdt = -self.rocket.Mu * z / r ** 3

        # Apply each perturbation
        for perturbation in self.perturbations:
            du_p, dv_p, dw_p = perturbation.calculate(Y, t, self.rocket)
            dudt += du_p
            dvdt += dv_p
            dwdt += dw_p

        # Apply the thrust force
        du_thrust, dv_thrust, dw_thrust, dmassdt = self.thrust_force.calculate(Y, t, self.rocket)
        dudt += du_thrust
        dvdt += dv_thrust
        dwdt += dw_thrust

        return [dxdt, dydt, dzdt, dudt, dvdt, dwdt, dmassdt]

    def apoapsis_parachute_event(self, t, Y):
        """
        Event to detect the apoapsis of the trajectory for parachute deployment.
        """
        return Y[5]

    apoapsis_parachute_event.terminal = True
    apoapsis_parachute_event.direction = -1  # Event triggers on descent (altitude decreasing)

    def main_parachute_event(self, t, Y):
        """
        Event to detect the altitude for main parachute deployment.
        """

        # Set the percentage of the peak altitude for the trigger and the minimum altitude (km) trigger if otherwise
        min_altitude_trigger = 0.3
        percentage_of_max_height = 0.1

        # Calculate the maximum altitude from the start of the simulation (Y at t=0)
        max_altitude_at_start = self.apoapsis - self.body_radius

        # Calculate percentage of max height to trigger the parachute
        trigger_altitude_based_on_max_height = max_altitude_at_start * percentage_of_max_height
        current_altitude = np.linalg.norm(Y[:3]) - self.body_radius

        # Trigger whichever condition is met first: 10% of max height or 300 meters
        trigger_altitude = max(trigger_altitude_based_on_max_height, min_altitude_trigger)

        # Event triggers when current altitude is less than or equal to the trigger altitude
        return current_altitude - trigger_altitude

    main_parachute_event.terminal = True
    main_parachute_event.direction = -1  # Event triggers on descent (altitude decreasing)

    def ground_impact_event(self, t, Y):
        """
        Detects when the rocket has crashed into the Earth's surface.
        """
        return np.linalg.norm(Y[:3]) - self.body_radius

    ground_impact_event.terminal = True  # Terminate entire simulation when the rocket crashes into the Earth's surface
    ground_impact_event.direction = -1  # Detect when the rocket is descending through the Earth's surface only
