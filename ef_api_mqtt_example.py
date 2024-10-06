"""
Example code to illustrate use of the Ecoflow Open API
- Login to API over HTTP using acceess and secret keys
- Obtain MQTT credentials via HTTP
- Connect to MQTT using obtained credentials
- Subscribe to /quota topic for a device (uses serial number)
- Log MQTT messages posted to the topic

By: Mark Hicks - 10/06/2024
"""

import hashlib
import hmac
import logging
import random
import ssl
import time

import paho.mqtt.client as mqtt
import requests


class MqttClient:
    def __init__(self, url, port, name, user, pwd):
        log.debug(f"MqttClient: {url}:{port} as {name}")
        self.url = url
        self.port = port
        self.name = name
        self.user = user
        self.pwd = pwd
        self.mqtt = mqtt.Client(name)
        self.resp = None

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            log.error(f"MQTT Connect: Response Code = {rc}")

    def on_message(self, client, userdata, msg):
        log.info("Received message on topic %s: %s", msg.topic, msg.payload)
        self.resp = msg.payload

    def connect(self):
        log.info(f"MQTT Connect: {self.url}:{self.port}...")
        try:
            self.mqtt.on_connect = self.on_connect
            self.mqtt.on_message = self.on_message
            self.mqtt.tls_set(cert_reqs=ssl.CERT_NONE)
            self.mqtt.username_pw_set(username=self.user, password=self.pwd)
            self.mqtt.connect(self.url, self.port, 60)
            self.mqtt.loop_start()
        except ssl.SSLError as e:
            log.error(f"MQTT Connect: SSL - {e}")
        except Exception as e:
            log.error(f"MQTT Connect: Unexpected - {e}")

    def disconnect(self):
        try:
            self.mqtt.loop_stop()
            self.mqtt.disconnect()
        except Exception as e:
            log.error(f"MQTT Disconnect: Unexpected - {e}")

    def subscribe(self, topic):
        log.debug(f"MQTT Subscribe: {topic}")
        try:
            self.mqtt.subscribe(topic)
        except Exception as e:
            log.error(f"MQTT Subscribe: Unexpected - {e}")

    def unsubscribe(self, topic):
        log.debug(f"MQTT UnSubscribe: {topic}")
        try:
            self.mqtt.unsubscribe(topic)
        except Exception as e:
            log.error(f"MQTT UnSubscribe: Unexpected - {e}")

    def publish(self, topic, payload):
        log.debug(f"MQTT Publish: {topic}")
        log.debug(f"MQTT Publish: payload {payload}")
        try:
            self.mqtt.publish(topic, payload)
        except Exception as e:
            log.error(f"MQTT Publish: Unexpected - {e}")


def hmac_sha256(data, key):
    hashed = hmac.new(
        key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).digest()
    return "".join(format(byte, "02x") for byte in hashed)


def get_qstring(params):
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def get_api(url, key, secret, params=None):
    nonce = str(random.randint(100000, 999999))
    timestamp = str(int(time.time() * 1000))
    headers = {"accessKey": key, "nonce": nonce, "timestamp": timestamp}
    sign_str = (get_qstring(params) + "&" if params else "") + get_qstring(headers)
    headers["sign"] = hmac_sha256(sign_str, secret)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        log.error(f"get_api: {response.text}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s, %(levelname)s, %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
    )
    log = logging.getLogger(__name__)

    # Note: Out side the US and in Europe use:
    # url = "https://api-e.ecoflow.com"
    url = "https://api-a.ecoflow.com"
    path = "/iot-open/sign/certification"

    # Provide your keys and device serial number below ...
    key = "Fp4SvIprYSDPXtYJidEtUAd1o"
    secret = "WIbFEKre0s6sLnh4ei7SPUeYnptHG6V"
    sn = "Y711DABCDEF01234"

    payload = get_api(f"{url}{path}", key, secret, {"sn": sn})
    data = payload.get("data")

    if data:
        log.debug("MQTT = %s", data)
        m_url = data["url"]
        port = int(data["port"])
        user = data["certificateAccount"]
        pwd = data["certificatePassword"]
        topic = f"/open/{user}/{sn}/quota"

        mqtt_client = MqttClient(m_url, port, f"test_{user}", user, pwd)
        mqtt_client.connect()
        mqtt_client.subscribe(topic)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Interrupted - Exiting...")
        except Exception as e:
            log.error(e)
        mqtt_client.disconnect()

    else:
        log.error("No MQTT Credentials returned!")
