import json
import random
import time
from datetime import datetime
from flask import Flask, Response, jsonify, render_template, request
from flask_mqtt import Mqtt
from datetime import datetime
#from flask_ngrok import run_with_ngrok

app = Flask(__name__)
#run_with_ngrok(app)
random.seed()

app.config["MQTT_BROKER_URL"] = "broker.emqx.io"
app.config["MQTT_BROKER_PORT"] = 1883
# app.config['MQTT_USERNAME'] = 'Your Username'
# app.config['MQTT_PASSWORD'] = 'Your Password'
app.config["MQTT_REFRESH_TIME"] = 1.0  # refresh time in seconds
try:
    mqtt = Mqtt(app)
except:
    print('timeout')
ph, nd, oxy = None, None, None


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):

    # Đăng ký kênh riêng biệt
    # mqtt.subscribe("tlqb/ND")
    # mqtt.subscribe("tlqb/PH")
    # mqtt.subscribe("tlqb/OXY")
    # while True:
    # mqtt.publish("PH", "70")
    # time.sleep(2)

    # Đăng ký tất cả các kênh
    mqtt.subscribe("#")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global ph, nd, oxy
    data = dict(topic=message.topic, payload=message.payload.decode())
    print(data)
    if message.topic == "iot/ND":
        nd = message.payload.decode()
    if message.topic == "iot/PH":
        ph = message.payload.decode()
    if message.topic == "iot/OXY":
        oxy = message.payload.decode()
    print(nd, ph, oxy, "****************************** \n")


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


@app.route("/")
def home():
    return render_template("home.html")
    # return render_template("index.html")


@app.route("/values")
def index():
    # return render_template("home.html")
    return render_template("index.html")


@app.route("/chart-data_ND")
def chart_data_ND():
    global nd

    def generate_random_data():

        while True:
            # mqtt.publish("PH", "70")
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value": nd,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype="text/event-stream")


@app.route("/chart-data_PH")
def chart_data_PH():
    global ph

    def generate_random_data():
        while True:
            # mqtt.publish("PH", "70")
            json_data = json.dumps(
                {
                    # "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value": ph,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype="text/event-stream")


@app.route("/chart-data_OXY")
def chart_data_OXY():
    global oxy

    def generate_random_data():
        while True:
            # mqtt.publish("PH", "70")
            json_data = json.dumps(
                {
                    # "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value": oxy,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype="text/event-stream")


@app.route("/_stuff", methods=["GET"])
def stuff():
    global ph, nd, oxy
    timenow = datetime.now()
    return jsonify(nd=nd, ph=ph, oxy=oxy, timenow=timenow)


if __name__ == "__main__":
    try:
        app.run(debug=True, threaded=True)
        #app.run(debug=True)
        #socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)
    except:
        print("Don't connecting")

