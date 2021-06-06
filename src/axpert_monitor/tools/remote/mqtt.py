import paho.mqtt.client as mqtt
import logging

MQTT_OK = 0
MQTT_CONN_ERROR = 1
MQTT_NOT_READY = 2
MQTT_UNKNOWN = 3


class MQTTCommunicator:
    """A class for communicating to a MQTT server"""

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        logging.info(f"MQTT connected with result code {str(rc)}")

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        logging.info("Subscribing to MQTT topics...")
        # client.subscribe("$SYS/#")
        client.subscribe("test")

    @staticmethod
    def on_message(client, userdata, msg):
        logging.debug(f"MQTT > {msg.topic}: {msg.payload}")

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        logging.info(f"MQTT subscribed with qos {granted_qos}.")

    def publish(self, topic: str, message: str) -> int:
        """
        Publishes a message to the desired MQTT topic.
        :param topic: The topic to publish to.
        :param message: The payload dict to send.
        :return: [MQTT_OK] If the message was sent successfully, [MQTT_CONN_ERROR] if there was an error while
        connecting to the server, [MQTT_NOT_READY] when the MQTT connection has not been initialized, and
        [MQTT_UNKNOWN], if there has been an unknown error while sending the message.
        """
        try:
            if self.client is not None and self.is_connected:
                self.client.publish(topic, payload=message)
                logging.info(f"Published payload on {topic}.")
                return MQTT_OK
            elif self.client is not None and not self.is_connected:
                return MQTT_CONN_ERROR
            elif self.client is None:
                return MQTT_NOT_READY
            else:
                return MQTT_UNKNOWN
        except:
            return MQTT_UNKNOWN

    def publish_dict(self, topic: str, payload: dict) -> int:
        """
        Publishes a dict to the desired MQTT topic.
        :param topic: The topic to publish to.
        :param payload: The payload dict to send.
        :return: [MQTT_OK] If the payload was sent successfully, [MQTT_CONN_ERROR] if there was an error while
        connecting to the server, [MQTT_NOT_READY] when the MQTT connection has not been initialized, and
        [MQTT_UNKNOWN], if there has been an unknown error while sending the payload.
        """
        try:
            if self.client is not None and self.is_connected:
                for key in payload:
                    self.client.publish(f"{topic}/{key}", payload=payload[key])
                logging.info(f"Published payload on {topic}.")
                return MQTT_OK
            elif self.client is not None and not self.is_connected:
                return MQTT_CONN_ERROR
            elif self.client is None:
                return MQTT_NOT_READY
            else:
                return MQTT_UNKNOWN
        except:
            return MQTT_UNKNOWN

    def __init__(self, address, port, keep_alive):
        """
        Initializes the MQTT communicator instance, and connects to the server.
        :param address: The address of the MQTT server
        :param port: The port to use for the communication
        :param keep_alive: The keep alive time for the communication
        """
        logging.debug("Getting MQTT settings...")

        logging.debug("Initializing MQTT...")
        self.client = mqtt.Client()
        self.client.on_connect = MQTTCommunicator.on_connect
        self.client.on_message = MQTTCommunicator.on_message
        self.client.on_subscribe = MQTTCommunicator.on_subscribe

        logging.debug("Connecting MQTT...")
        try:
            self.client.connect(address, port=port, keepalive=keep_alive)

            logging.debug("Starting MQTT loop...")
            self.client.loop_start()

            logging.info("MQTT ready.")
            self.is_connected = True
        except:
            logging.error("Could not connect to the MQTT server.")
            self.is_connected = False
