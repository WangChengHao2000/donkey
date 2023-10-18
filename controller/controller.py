from donkeycar.utils import logging
import torch
import torchvision.transforms as transforms
import cv2

from dl.models import AutoDriveNet

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

        steering_angle, frame = draw_line(image)

        if steering_angle == None:
            return [frame, steering, throttle]

        return [frame, steering_angle, throttle]


class CVTwoLaneController(object):
    def __init__(self):
        print("CVController init...")

    def run(self, image, steering, throttle):
        from cv.two_line_tools import draw_line

        steering_angle, frame = draw_line(image)

        if steering_angle == None:
            return [frame, steering, throttle]

        return [frame, steering_angle, throttle]


class DLController(object):
    def __init__(self, checkpoint="./results/checkpoint.pth"):
        self.checkpoint = checkpoint
        self.model = AutoDriveNet()
        if checkpoint is not None:
            self.checkpoint = torch.load(self.checkpoint)
            self.model.load_state_dict(self.checkpoint["model"])

    def run(self, image, steering, throttle):
        self.model.eval()
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        transformations = transforms.Compose(
            [
                transforms.ToTensor(),
            ]
        )
        frame = transformations(frame)
        frame = frame.reshape(1, 3, 120, 160)
        steering_angle = self.model(frame)
        print(steering_angle)
        return [steering_angle, throttle]
