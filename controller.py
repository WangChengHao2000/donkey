import math
import cv2

from donkeycar.utils import logging

logger = logging.getLogger(__name__)


class Controller(object):
    def __init__(self):
        logger.info("Controller init...")
        self.right = True

    def run(self, image, steering, throttle):
        logger.info(f"get image input: {str(type(image))}")
        if self.right:
            steering += 0.1
        else:
            steering -= 0.1
        if steering > 1 or steering < -1:
            self.right = not self.right
        logger.info(f"steering: {steering}")
        logger.info(f"throttle: {throttle}")
        return [steering, throttle]


class BackendController(object):
    def __init__(self):
        print("BackendController init...")

    def run(self, image, steering, throttle):
        import requests
        import json

        data = {"image": image, "steering": steering, "throttle": throttle}
        response = requests.post("http://127.0.0.1:8887/get", data=data)
        result = json.loads(response.text)

        return [result["steering"], result["throttle"]]


class CVController(object):
    def __init__(self):
        print("CVController init...")

    def run(self, image, steering, throttle):
        from cv.tools import draw_line

        lane_lines, frame = draw_line(image)
        height, width, _ = frame.shape

        if lane_lines == None or len(lane_lines) == 0:
            return [frame, steering, throttle]

        _, _, x2, _ = lane_lines[0][0]
        mid = int(width / 2)
        x_offset = x2 - mid
        y_offset = int(height / 2)
        angle_to_mid_radian = math.atan(x_offset / y_offset)
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
        steering_angle = angle_to_mid_deg / 45.0
        print("steering_angle: " + str(steering_angle))

        return [frame, steering_angle, throttle]


class CVTwoLaneController(object):
    def __init__(self):
        print("CVController init...")

    def run(self, image, steering, throttle):
        from cv.two_line_tools import draw_line
