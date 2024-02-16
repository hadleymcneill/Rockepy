"""
This module contains the class for propagating the rocket trajectory of the orbital ascent.
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
        self.rocket.gravity_turn_initiated = False
        self.rocket.gravity_turn_operational = False
        self.rocket.current_stage = -1

    def propagate(self):
        """
        Propagates the rocket's trajectory considering the provided perturbations.
        Automatically adapts to the number of stages specified for the rocket.
        """

        # Initialise the state vector, state matrix combining all phases, and the time vector.
        U0 = np.concatenate((self.rocket.position, self.rocket.velocity, [self.rocket.mass]))
        combined_Y = np.array([]).reshape(0, U0.shape[0])
        combined_t_eval = np.array([])

        # Initialise variables for section indices used to split the trajectory into sections for each phase.
        section_indices = []
        start_index = 0

        # Propagate the trajectory for each stage
        for i in range(len(self.rocket.burnout_times) + 1):
            if i == 0:
                t_start = 0
            else:
                t_start = self.rocket.burnout_times[i - 1]
                U0[-1] -= self.rocket.empty_mass[i - 1]  # Reduce the mass by the empty_mass of the previous stage

            if i < len(self.rocket.burnout_times):
                t_end = self.rocket.burnout_times[i]
            else:
                t_end = self.rocket.burnout_times[-1] + self.rocket.final_coast  # Add final coast after last stage

            self.rocket.current_stage += 1

            # Propagate the trajectory for the current stage and combine the trajectory with the previous stages
            t_eval = np.arange(t_start, t_end, self.rocket.propagation_time_step)
            sol = solve_ivp(self._state_derivatives, (t_start, t_end), U0, method='RK45', t_eval=t_eval,
                            events=self.ground_impact_event)
            Y_sol = sol.y.T
            combined_Y = np.concatenate((combined_Y, Y_sol), axis=0)

            # Check if the rocket has crashed into the surface, terminates the simulation and readjusts the time vector
            if sol.status == 1:
                print(f"Warning: OrbitalRocket stage {i + 1} has crashed into the Earth's surface. Simulation terminated.") if not self.rocket.optimise_mode else None
                t_eval = np.arange(t_start, round(sol.t[-1], 2) + self.rocket.propagation_time_step,
                                   self.rocket.propagation_time_step)
                readjustment_error = abs(len(t_eval) - len(Y_sol))
                combined_t_eval_i = np.concatenate((combined_t_eval, t_eval))
                combined_t_eval = combined_t_eval_i[
                                  :-readjustment_error] if readjustment_error > 0 else combined_t_eval_i
                end_index = start_index + len(t_eval)
                section_indices.append((start_index, end_index))
                break

            # Combine the time vector and update the section indices
            combined_t_eval = np.concatenate((combined_t_eval, t_eval))
            end_index = start_index + len(t_eval)
            section_indices.append((start_index, end_index))
            start_index = end_index

            # Update initial state of the next phase to the final state from the current phase
            U0 = sol.y[:, -1]

        # Update the rocket's state vector, time vector, and section indices once the propagation is complete
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

    def ground_impact_event(self, t, Y):
        """
        Detects when the rocket has crashed into the Earth's surface.
        """
        return np.linalg.norm(Y[:3]) - self.body_radius

    ground_impact_event.terminal = True  # Terminate entire simulation when the rocket crashes into the Earth's surface
    ground_impact_event.direction = -1  # Detect when the rocket is descending through the Earth's surface only
