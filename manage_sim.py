import donkeycar as dk
from donkeycar.parts.tub_v2 import TubWriter
from donkeycar.parts.datastore import TubHandler


def run(cfg):
    V = dk.vehicle.Vehicle()

    add_simulator(V, cfg)
    add_controller(V, cfg)
    add_record(V, cfg)

    V.start(rate_hz=10, max_loop_count=300)


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
    elif cfg.CONTROLLER_TYPE == "DL":
        from controller.controller import DLController

        V.add(
            DLController(),
            inputs=["cam/image_array", "steering", "throttle"],
            outputs=["steering", "throttle"],
        )
    else:
        raise (Exception("Unknown controller type: %s" % cfg.CONTROLLER_TYPE))


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
    cfg = dk.load_config(myconfig="myconfig_sim_dl.py")
    run(cfg)
