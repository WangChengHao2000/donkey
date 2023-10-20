import donkeycar as dk
from donkeycar.parts.controller import LocalWebController
from donkeycar.parts.transform import Lambda
from donkeycar.parts.tub_v2 import TubWriter
from donkeycar.parts.datastore import TubHandler
from donkeycar.utils import logging


def run(cfg):
    V = dk.vehicle.Vehicle()

    add_camera(V, cfg)
    add_controller(V, cfg)
    add_drive(V, cfg)
    add_record(V, cfg)
    
    V.start(rate_hz=10, max_loop_count=200)


def add_camera(V, cfg):
    if cfg.CAMERA_TYPE == "PICAM":
        from donkeycar.parts.camera import PiCamera

        cam = PiCamera(
            image_w=cfg.IMAGE_W,
            image_h=cfg.IMAGE_H,
            image_d=cfg.IMAGE_DEPTH,
            vflip=cfg.CAMERA_VFLIP,
            hflip=cfg.CAMERA_HFLIP,
        )
        V.add(cam, inputs=[], outputs=["cam/image_array"], threaded=True)
    else:
        raise (Exception("Unknown camera type: %s" % cfg.CAMERA_TYPE))


def add_user_controller(V, cfg):
    V.add(
        LocalWebController(port=cfg.WEB_CONTROL_PORT, mode=cfg.WEB_INIT_MODE),
        inputs=["cam/image_array", 0, None, None],
        outputs=[
            "steering",
            "throttle",
            "mode",
            "recording",
            "buttons",
        ],
        threaded=True,
    )


def add_controller(V, cfg):
    V.mem["steering"] = 0
    V.mem["throttle"] = 0.1

    if cfg.CONTROLLER_TYPE == "CV":
        from controller.controller import CVController

        V.add(
            CVController(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["cam/image_array", "steering", "throttle"],
        )
    elif cfg.CONTROLLER_TYPE == "CVTWO":
        from controller.controller import CVTwoLaneController

        V.add(
            CVTwoLaneController(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["cam/image_array", "steering", "throttle"],
        )
    elif cfg.CONTROLLER_TYPE == "BACKEND":
        from controller.controller import BackendController

        V.add(
            BackendController(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    else:
        raise (Exception("Unknown controller type: %s" % cfg.CONTROLLER_TYPE))


def add_drive(V, cfg):
    if cfg.DRIVE_TRAIN_TYPE == "PWM_STEERING_THROTTLE":
        from donkeycar.parts import pins
        from donkeycar.parts.actuator import (
            PWMSteering,
            PWMThrottle,
            PulseController,
        )

        dt = cfg.PWM_STEERING_THROTTLE
        steering_controller = PulseController(
            pwm_pin=pins.pwm_pin_by_id(dt["PWM_STEERING_PIN"]),
            pwm_scale=dt["PWM_STEERING_SCALE"],
            pwm_inverted=dt["PWM_STEERING_INVERTED"],
        )
        steering = PWMSteering(
            controller=steering_controller,
            left_pulse=dt["STEERING_LEFT_PWM"],
            right_pulse=dt["STEERING_RIGHT_PWM"],
        )
        throttle_controller = PulseController(
            pwm_pin=pins.pwm_pin_by_id(dt["PWM_THROTTLE_PIN"]),
            pwm_scale=dt["PWM_THROTTLE_SCALE"],
            pwm_inverted=dt["PWM_THROTTLE_INVERTED"],
        )
        throttle = PWMThrottle(
            controller=throttle_controller,
            max_pulse=dt["THROTTLE_FORWARD_PWM"],
            zero_pulse=dt["THROTTLE_STOPPED_PWM"],
            min_pulse=dt["THROTTLE_REVERSE_PWM"],
        )
        V.add(steering, inputs=["steering"], threaded=True)
        V.add(throttle, inputs=["throttle"], threaded=True)
    else:
        raise (Exception("Unknown drive type: %s" % cfg.DRIVE_TRAIN_TYPE))


def add_record(V, cfg):
    if cfg.TUB_RECORDING:
        tub_path = (
            TubHandler(path=cfg.DATA_PATH).create_tub_path()
            if cfg.AUTO_CREATE_NEW_TUB
            else cfg.DATA_PATH
        )
        inputs = ["cam/image_array", "steering", "throttle"]
        types = ["image_array", "float", "float"]
        meta = getattr(cfg, "METADATA", [])
        tub_writer = TubWriter(tub_path, inputs=inputs, types=types, metadata=meta)
        V.add(
            tub_writer,
            inputs=inputs,
            outputs=["tub/num_records"],
        )


if __name__ == "__main__":
    cfg = dk.load_config()
    run(cfg)
