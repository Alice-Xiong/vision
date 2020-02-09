import os
from pathlib import Path
from source.module import Module
import math


class AbsoluteAngleCalculation(Module):
    def __init__(self, state=None):
        self.working_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(self.working_dir, state=state)

    def process(self, panel, distance, encoder_data):
        """
        converts the panel, distance and pitch into real world coordinates to send to embedded
        :param panel: An object that contains the center of the target panel
        :param distance: the distance from the robot to the panel
        :param encoder_data: the pitch and yaw of the barrel
        :return: (theta, phi, shoot) pitch angle, yaw angle, shoot or not boolean
        """
        target_x, target_y = panel.x, panel.y  # Will likely need to change when panel object is changed
        gimbal_x = encoder_data.x  # depends of encoder_data format
        gimbal_y = encoder_data.y  # depends of encoder_data format
        absolute_x = target_x - (self.properties["camera_fov_x"] / 2) + gimbal_x
        absolute_y = target_y - (self.properties["camera_fov_y"] / 2) + gimbal_y
        absolute_y = self.compensate_for_distance(absolute_y, distance, gimbal_y)
        x_diff = gimbal_x - absolute_x
        y_diff = gimbal_y - absolute_y
        accuracy = math.sqrt(x_diff ** 2 + y_diff ** 2)
        shoot = accuracy < self.properties["accuracy_cutoff"]
        return absolute_x, absolute_y, shoot

    def compensate_for_distance(self, absolute_y, distance, pitch):  # TODO: test if this works
        x = distance * math.cos(absolute_y)
        y = distance * math.sin(absolute_y)
        g = 9.8  # gravity
        v = self.properties["firing_velocity"]
        tan_theta = (-x + math.sqrt(x ** 2 - 4 * (g ** 2 * x ** 2 / (4 * v ** 4) - x * g * y / (2 * v ** 2)))) / (
                g * x / v ** 2)
        theta = math.atan(tan_theta)
        return theta
