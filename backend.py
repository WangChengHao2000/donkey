from flask import Flask, request
import random

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/get", methods=["POST"])
    def get():
        steering = int(request.form["steering"])
        throttle = int(request.form["throttle"])
        steering += random.randint(-10, 10)
        throttle += random.randint(-100, 100)
        return {"steering": steering, "throttle": throttle}

    app.run(host="127.0.0.1", port=8887)
