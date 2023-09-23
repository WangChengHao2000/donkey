import time
import random


class Controller(object):
    def __init__(self):
        print("Controller init...")

    def run(self, image, steering, throttle):
        print("get input")
        print(type(image))
        steering += random.randint(0, 10)
        throttle += random.randint(0, 10)
        print("steering: %d" % steering)
        print("throttle: %d" % throttle)
        time.sleep(0.3)
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


if __name__ == "__main__":
    from PIL import Image
    import numpy as np

    controller = BackendController()
    image = np.array(Image.new("RGB", (256, 256)))
    controller.run(image=image, steering=20, throttle=300)