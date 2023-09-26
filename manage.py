import donkeycar as dk
from donkeycar.parts.controller import LocalWebController
from donkeycar.parts.transform import Lambda
from donkeycar.utils import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run(cfg):
    V = dk.vehicle.Vehicle()

    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    add_simulator(V, cfg)

    add_camera(V, cfg)

    if cfg.USER_CONTROLLER:
        add_user_controller(V, cfg)
    else:
        add_controller(V, cfg)

    add_drive(V, cfg)

    if cfg.USER_CONTROLLER:
        V.start(rate_hz=10)
    else:
        V.start(rate_hz=10, max_loop_count=100)


def add_simulator(V, cfg):
    if cfg.DONKEY_GYM:
        from donkeycar.parts.dgym import DonkeyGymEnv

        gym = DonkeyGymEnv(
            cfg.DONKEY_SIM_PATH,
            host=cfg.SIM_HOST,
            env_name=cfg.DONKEY_GYM_ENV_NAME,
            conf=cfg.GYM_CONF,
        )

        V.add(
            gym,
            inputs=["steering", "throttle"],
            outputs=["cam/image_array"],
            threaded=True,
        )


def add_camera(V, cfg):
    if not cfg.DONKEY_GYM:
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
        elif cfg.CAMERA_TYPE == "MOCK":
            from donkeycar.parts.camera import MockCamera

            cam = MockCamera(
                image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH
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
    if not cfg.DONKEY_GYM:
        V.mem["steering"] = 0
        V.mem["throttle"] = 0.2
    else:
        V.mem["steering"] = 0
        V.mem["throttle"] = 0.1

    if cfg.CONTROLLER_TYPE == "MOCK":
        from controller import Controller

        V.add(
            Controller(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    elif cfg.CONTROLLER_TYPE == "BACKEND":
        from controller import BackendController

        V.add(
            BackendController(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    else:
        raise (Exception("Unknown controller type: %s" % cfg.CONTROLLER_TYPE))


def add_drive(V, cfg):
    if not cfg.DONKEY_GYM:
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
        elif cfg.DRIVE_TRAIN_TYPE == "MOCK":
            V.add(
                Lambda(lambda v: print("execute steering: %d" % v)), inputs=["steering"]
            )
            V.add(
                Lambda(lambda v: print("execute throttle: %d" % v)), inputs=["throttle"]
            )
        else:
            raise (Exception("Unknown drive type: %s" % cfg.DRIVE_TRAIN_TYPE))


if __name__ == "__main__":
    cfg = dk.load_config()
    run(cfg)
