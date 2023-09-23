import donkeycar as dk
from donkeycar.parts.transform import Lambda


def run(cfg):
    V = dk.vehicle.Vehicle()

    add_camera(V, cfg)
    add_controller(V, cfg)
    add_drive(V, cfg)

    V.start(rate_hz=3, max_loop_count=10)


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
        V.add(cam, inputs=[], outputs=["image"], threaded=True)
    elif cfg.CAMERA_TYPE == "MOCK":
        from donkeycar.parts.camera import MockCamera

        cam = MockCamera(
            image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH
        )
        V.add(cam, inputs=[], outputs=["image"], threaded=True)
    else:
        raise (Exception("Unknown camera type: %s" % cfg.CAMERA_TYPE))


def add_controller(V, cfg):
    if cfg.CONTROLLER_TYPE == "MOCK":
        from controller import Controller

        V.mem["steering"] = int((cfg.STEERING_LEFT_PWM + cfg.STEERING_RIGHT_PWM) / 2)
        V.mem["throttle"] = cfg.THROTTLE_STOPPED_PWM
        V.add(
            Controller(),
            inputs=["image", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    elif cfg.CONTROLLER_TYPE == "BACKEND":
        from controller import BackendController

        V.mem["steering"] = int((cfg.STEERING_LEFT_PWM + cfg.STEERING_RIGHT_PWM) / 2)
        V.mem["throttle"] = cfg.THROTTLE_STOPPED_PWM
        V.add(
            BackendController(),
            inputs=["image", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    else:
        raise (Exception("Unknown controller type: %s" % cfg.CONTROLLER_TYPE))


def add_drive(V, cfg):
    if cfg.DRIVE_TRAIN_TYPE == "PWM_STEERING_THROTTLE":
        from donkeycar.parts import pins
        from donkeycar.parts.actuator import PWMSteering, PWMThrottle, PulseController

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
    elif cfg.DRIVE_TRAIN_TYPE == "MOCK":
        V.add(Lambda(lambda v: print("execute steering: %d" % v)), inputs=["steering"])
        V.add(Lambda(lambda v: print("execute throttle: %d" % v)), inputs=["throttle"])
    else:
        raise (Exception("Unknown drive type: %s" % cfg.DRIVE_TRAIN_TYPE))


if __name__ == "__main__":
    cfg = dk.load_config()
    run(cfg)
