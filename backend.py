from flask import Flask, request
import random

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/get", methods=["POST"])
    def get():
        steering = float(request.form["steering"])
        throttle = float(request.form["throttle"])
        steering += random.randint(-1, 1) * 0.1
        throttle += random.randint(-1, 1) * 0.1
        return {"steering": steering, "throttle": throttle}

    app.run(host="127.0.0.1", port=8887)
