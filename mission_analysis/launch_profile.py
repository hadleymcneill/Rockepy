"""
This file contains the class for the reporting the results of the propagation of the rocket.
"""

import numpy as np
import pyvista as pv
from pyvista import examples
import matplotlib.pyplot as plt
from utilities.utilities import set_axes_equal
from aerodynamics.atmospheric_model import atmospheric_density
from utilities.utilities import normalise_value
from pathlib import Path

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 14


class PropagationProfile:
    def __init__(self, rocket):
        """
        Class for reporting the results of the rocket's propagation profile.
        """
        self.rocket = rocket

        self.latitude = self.rocket.launch_site[0]
        self.longitude = self.rocket.launch_site[1]
        self.body_radius = 6371

        # Calculate the rocket's position, velocity, altitude, mass, and acceleration for reporting
        self.rocket.velocity = self.rocket.Y[:, 3:6]
        self.rocket.velocity_magnitude = np.linalg.norm(self.rocket.velocity, axis=1)
        self.rocket.position = self.rocket.Y[:, 0:3]
        self.rocket.position_magnitude = np.linalg.norm(self.rocket.position, axis=1)
        self. x, self.y, self.z = self.rocket.position[:, 0], self.rocket.position[:, 1], self.rocket.position[:, 2]
        self.rocket.altitude = self.rocket.position_magnitude - self.body_radius
        self.rocket.mass_history = self.rocket.Y[:, 6]
        self.rocket.acceleration = np.gradient(self.rocket.velocity_magnitude * 1000, self.rocket.t_eval)

        # Calculate the flight path angle
        v_r = np.sum(self.rocket.velocity * self.rocket.position, axis=1) / self.rocket.position_magnitude
        v_t_squared = self.rocket.velocity_magnitude ** 2 - (v_r ** 2)
        v_t = np.sqrt(np.maximum(v_t_squared, 0))
        self.rocket.flight_path_angle = np.degrees(np.arctan2(v_r, v_t))

        #dynamic pressure
        density_history = np.array([atmospheric_density(alt) for alt in self.rocket.altitude])
        self.rocket.dynamic_pressure = 0.5 * density_history * (self.rocket.velocity_magnitude * 1000) ** 2


    def report_suborbital(self):
        self.flight_type = 'suborbital'
        self.colours = ['red', 'green', 'blue', 'black']
        self.report_velocity()
        self.report_acceleration()
        self.report_altitude()
        self.report_mass()
        self.report_flight_path_angle()
        self.report_dynamic_pressure()
        self.propagation_profile_suborbital()
        plt.show()

    def report_orbital(self):
        self.flight_type = 'orbital'
        self.colours = ['red', 'green', 'cyan', 'blue']
        self.report_velocity()
        self.report_acceleration()
        self.report_altitude()
        self.report_mass()
        self.report_flight_path_angle()
        self.report_dynamic_pressure()
        self.propagation_profile_orbital_2D()
        self.propagation_profile_orbital_true_view()
        plt.show()

    def propagation_profile_orbital_true_view(self):
        """
        Advanced 3D plot of the propagation profile of the orbital rocket showing view from above Earth.
        """

        # Setup light
        light = pv.Light()
        light.set_direction_angle(30, -20)

        # Load Earth and its texture
        earth = examples.planets.load_earth(radius=6371)
        project_root = Path(__file__).resolve().parent.parent
        assets_dir = project_root / 'utilities' / 'assets'
        earth_texture_path = assets_dir / '16k_earth_clouds_map.jpeg'
        earth_texture = pv.read_texture(str(earth_texture_path))

        # Determine inclination, normalised to consider latitude constraints
        normalised_inclination = normalise_value(self.rocket.target_inclination, self.latitude, 180 - self.latitude, 0, 180)

        # Launch location and inclination
        rot = earth.rotate_z(-self.longitude, inplace=False) # Determines longitude
        rot = rot.rotate_y(90-self.latitude, inplace=False) # Determines latitude
        rot = rot.rotate_z(180 - normalised_inclination, inplace=False) # Determines inclination

        # Create plotter with Earth and stars
        pl = pv.Plotter(lighting="none", window_size=(3000, 1600))
        pl.add_mesh(rot, texture=earth_texture, smooth_shading=True)
        cubemap = examples.download_cubemap_space_16k()
        _ = pl.add_actor(cubemap.to_skybox())
        pl.set_environment_texture(cubemap, True)

        # Add the rocket's trajectory phase by phase
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            points = np.column_stack((self.x[start_idx:end_idx], self.y[start_idx:end_idx], self.z[start_idx:end_idx]))
            line = pv.lines_from_points(points)
            pl.add_mesh(line, color=self.colours[i % len(self.colours)], line_width=5)

        # Set the camera position and focal point to view the trajectory
        buffer = 100
        bounds = [np.min(self.x) - buffer, np.max(self.x) + buffer,
                  np.min(self.y) - buffer, np.max(self.y) + buffer,
                  np.min(self.z) - buffer, np.max(self.z) + buffer]

        pl.camera.position = [(bounds[1] + bounds[0]) / 2, bounds[3] + (bounds[3] - bounds[2]),
                              (bounds[5] + bounds[4]) / 2]
        pl.camera.focal_point = [(bounds[1] + bounds[0]) / 2, (bounds[3] + bounds[2]) / 2, (bounds[5] + bounds[4]) / 2]
        pl.show()

    def propagation_profile_orbital_2D(self):
        """
        Plot the propagation profile of the orbital rocket in 2D.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.y[start_idx:end_idx], self.z[start_idx:end_idx], color=self.colours[i % len(self.colours)],
                    linewidth=1.5, label=labels[i])

        # Dynamically calculate buffer based on trajectory spread
        y_range = max(self.y) - min(self.y)
        z_range = max(self.z) - min(self.z)
        avg_range = (y_range + z_range) / 2
        buffer = avg_range * 0.1  # Set buffer to 10% of average range

        # Adjust axes limits to focus on the trajectory
        min_y, max_y = min(self.y) - buffer, max(self.y) + buffer
        min_z, max_z = min(self.z) - buffer, max(self.z) + buffer
        ax.set_xlim(min_y, max_y)
        ax.set_ylim(min_z, max_z)

        # Draw Earth's surface and atmosphere
        earth_circle = plt.Circle((0, 0), 6371, color='green', fill=True)
        earth_atmosphere_circle = plt.Circle((0, 0), 6371+100, color='lightblue', fill=True, alpha=0.3)
        ax.add_patch(earth_circle)
        ax.add_patch(earth_atmosphere_circle)
        ax.set_aspect('equal')
        ax.legend(labels, loc='best')
        ax.set_title('2D Orbital Trajectory', fontsize=18)
        plt.grid(True)

    def propagation_profile_suborbital(self):
        """
        Plot the propagation profile of the suborbital rocket in 3D with 2D projections against the walls and floor.
        """
        fig3d = plt.figure(figsize=(15, 8))
        ax3d = fig3d.add_subplot(111, projection='3d')
        labels = self._get_legend_labels()  # Assuming this method returns a list of labels for the legend
        max_range = np.array(
            [self.x.max() - self.x.min(), self.y.max() - self.y.min(), self.rocket.altitude.max() - self.rocket.altitude.min()]).max() / 2.0
        mid_x = (self.x.max() + self.x.min()) * 0.5
        mid_y = (self.y.max() + self.y.min()) * 0.5
        mid_z = (self.rocket.altitude.max() + self.rocket.altitude.min()) * 0.5

        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # 3D trajectory
            ax3d.plot(self.x[start_idx:end_idx], self.y[start_idx:end_idx], self.rocket.altitude[start_idx:end_idx],
                      color=self.colours[i % len(self.colours)], linewidth=1.5, linestyle='dashed', label=labels[i])

        ax3d.legend(labels, loc='best')

        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Projections
            ax3d.plot(self.x[start_idx:end_idx], self.y[start_idx:end_idx],
                      np.full_like(self.x[start_idx:end_idx], mid_z - max_range),
                      color=self.colours[i % len(self.colours)], linewidth=2.0, alpha=0.5)
            ax3d.plot(self.x[start_idx:end_idx], np.full_like(self.y[start_idx:end_idx], mid_y + max_range),
                      self.rocket.altitude[start_idx:end_idx],
                      color=self.colours[i % len(self.colours)], linewidth=2.0, alpha=0.5)
            ax3d.plot(np.full_like(self.x[start_idx:end_idx], mid_x - max_range), self.y[start_idx:end_idx],
                      self.rocket.altitude[start_idx:end_idx],
                      color=self.colours[i % len(self.colours)], linewidth=2.0, alpha=0.5)

        # Set plot limits
        ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
        ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
        ax3d.set_zlim(mid_z - max_range, mid_z + max_range)

        set_axes_equal(ax3d)  # This will need to be adjusted, as it may interfere with the projections
        ax3d.set_xlabel('X (km)', fontsize=10)
        ax3d.set_ylabel('Y (km)', fontsize=10)
        ax3d.set_zlabel('Z (km)', fontsize=10)
        ax3d.set_title('Suborbital Trajectory', fontsize=18)

    def report_velocity(self):
        """
        Report the velocity of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.velocity_magnitude[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])

        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Velocity (km/s)', fontsize=14)
        ax.set_title('Velocity Over Time', fontsize=18)
        ax.grid(True)

    def report_acceleration(self):
        """
        Report the acceleration of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.acceleration[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])
        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Acceleration (m/s)', fontsize=14)
        ax.set_title('Acceleration Over Time', fontsize=18)
        ax.grid(True)

    def report_altitude(self):
        """
        Report the altitude of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.altitude[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])
        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Altitude (km)', fontsize=14)
        ax.set_title('Altitude Over Time', fontsize=18)
        ax.grid(True)

    def report_mass(self):
        """
        Report the mass of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.mass_history[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])
        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Mass (kg)', fontsize=14)
        ax.set_title('Mass Over Time', fontsize=18)
        ax.grid(True)

    def report_flight_path_angle(self):
        """
        Report the flight path angle of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.flight_path_angle[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])
        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Flight Path Angle (degrees)', fontsize=14)
        ax.set_title('Flight Path Angle Over Time', fontsize=18)
        ax.grid(True)

    def report_dynamic_pressure(self):
        """
        Report the flight path angle of the rocket over time for each phase of the trajectory.
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        labels = self._get_legend_labels()
        for i, (start_idx, end_idx) in enumerate(self.rocket.section_indices):
            # Plot the phase of the rocket's trajectory
            ax.plot(self.rocket.t_eval[start_idx:end_idx], self.rocket.dynamic_pressure[start_idx:end_idx],
                    color=self.colours[i % len(self.colours)], linewidth=1.5, label=labels[i])
        ax.legend(labels, loc='best')
        ax.set_xlabel('Time (s)', fontsize=14)
        ax.set_ylabel('Dynamic Pressure (N/m^2)', fontsize=14)
        ax.set_title('Dynamic Pressure Over Time', fontsize=18)
        ax.grid(True)

    def _get_legend_labels(self):
        """
        Returns a list of legend labels based on the flight type.
        """
        if self.flight_type == 'suborbital':
            # Defined phases for suborbital flight
            return ['Ascent', 'Coast', 'Drogue Parachute', 'Main Parachute']
        elif self.flight_type == 'orbital':
            labels = []
            for i in range(len(self.rocket.section_indices)):
                label = f'Stage {i + 1}' if i < len(self.rocket.section_indices) - 1 else 'Orbit Insertion'
                labels.append(label)
            return labels
