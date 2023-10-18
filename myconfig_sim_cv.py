DRIVE_TRAIN_TYPE = "PWM_STEERING_THROTTLE"

CONTROLLER_TYPE = "CV"  # (MOCK|CV|CVTWO|BACKEND)
BACKEND_TYPE = "LOCAL" # (LOCAL|REMOTE)
REMOTE_IP = None

TUB_RECORDING = True

DONKEY_GYM = True
DONKEY_SIM_PATH = "D:\projects\DonkeySimWin\donkey_sim.exe"
DONKEY_GYM_ENV_NAME = "donkey-generated-roads-v0"


import os

CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'cv/data')