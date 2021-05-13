from typing import Any, Optional
import paho.mqtt.client as mqtt
import logging

client: Optional[mqtt.Client] = None


def on_connect(client, userdata, flags, rc):
    logging.info(f"MQTT connected with result code {str(rc)}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    logging.info("Subscribing to MQTT topics...")
    # client.subscribe("$SYS/#")
    client.subscribe("test")


def on_message(client, userdata, msg):
    logging.debug(f"MQTT > {msg.topic}: {msg.payload}")


def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"MQTT subscribed with qos {granted_qos}.")


def mqtt_publish(topic, message):
    if client is not None:
        client.publish(topic, payload=message)
        logging.info(f"Published payload on {topic}.")


def mqtt_connect(address, port, keepalive):
    global client
    logging.debug("Initializing MQTT...")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    logging.debug("Connecting MQTT...")
    client.connect(address, port=port, keepalive=keepalive)

    logging.debug("Starting MQTT loop...")
    client.loop_start()


def mqtt_setup(configuration: dict[str, Any]):
    if "mqtt_address" in configuration:
        logging.debug("Getting MQTT settings...")
        address = configuration["mqtt_address"]
        port = configuration["mqtt_port"]
        keepalive = configuration["mqtt_keepalive"]

        mqtt_connect(address, port, keepalive)

        logging.info("MQTT ready.")
    else:
        logging.info("MQTT is disabled.")
