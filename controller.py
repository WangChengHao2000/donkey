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
