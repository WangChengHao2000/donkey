import donkeycar as dk
from donkeycar.parts.transform import Lambda


def run(cfg):
    V = dk.vehicle.Vehicle()
    add_camera(V, cfg)
    add_controller(V, cfg)
    add_drive(V, cfg)

    V.start(rate_hz=3, max_loop_count=3)


def add_camera(V, cfg):
    cam = None

    if cfg.CAMERA_TYPE == "PICAM":
        from donkeycar.parts.camera import PiCamera
        cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH,
                       vflip=cfg.CAMERA_VFLIP, hflip=cfg.CAMERA_HFLIP)
    elif cfg.CAMERA_TYPE == "MOCK":
        from donkeycar.parts.camera import MockCamera
        cam = MockCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
    else:
        raise (Exception("Unknown camera type: %s" % cfg.CAMERA_TYPE))

    if cam:
        V.add(cam, inputs=[], outputs=['image'], threaded=True)


def add_controller(V, cfg):
    from controller import Controller
    V.mem['steering'] = 0
    V.mem['throttle'] = 0
    V.add(Controller(), inputs=['image', 'steering', 'throttle'], outputs=['steering', 'throttle'])


def add_drive(V, cfg):
    drive = None

    from donkeycar.parts import pins
    from donkeycar.parts.actuator import PWMSteering, PWMThrottle, PulseController

    if cfg.DRIVE_TRAIN_TYPE == "PWM_STEERING_THROTTLE":
        dt = cfg.PWM_STEERING_THROTTLE
        steering_controller = PulseController(
            pwm_pin=pins.pwm_pin_by_id(dt["PWM_STEERING_PIN"]),
            pwm_scale=dt["PWM_STEERING_SCALE"],
            pwm_inverted=dt["PWM_STEERING_INVERTED"])
        steering = PWMSteering(controller=steering_controller,
                               left_pulse=dt["STEERING_LEFT_PWM"],
                               right_pulse=dt["STEERING_RIGHT_PWM"])
        throttle_controller = PulseController(
            pwm_pin=pins.pwm_pin_by_id(dt["PWM_THROTTLE_PIN"]),
            pwm_scale=dt["PWM_THROTTLE_SCALE"],
            pwm_inverted=dt['PWM_THROTTLE_INVERTED'])
        throttle = PWMThrottle(controller=throttle_controller,
                               max_pulse=dt['THROTTLE_FORWARD_PWM'],
                               zero_pulse=dt['THROTTLE_STOPPED_PWM'],
                               min_pulse=dt['THROTTLE_REVERSE_PWM'])
        V.add(steering, inputs=['steering'], threaded=True)
        V.add(throttle, inputs=['throttle'], threaded=True)
    elif cfg.DRIVE_TRAIN_TYPE == "MOCK":
        V.add(Lambda(lambda v: print('steering: %d' % v)), inputs=['steering'])
        V.add(Lambda(lambda v: print('throttle: %d' % v)), inputs=['throttle'])
    else:
        raise (Exception("Unknown drive type: %s" % cfg.DRIVE_TRAIN_TYPE))


if __name__ == '__main__':
    cfg = dk.load_config()
    run(cfg)
