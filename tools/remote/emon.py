from requests.models import Response
import json
import requests


class EmonCMSInstance:
    """A class for defining the connection to an EmonCMS instance"""

    def __init__(self, url, api_key):
        """
        Initializes the EmonCMS instance
        :param url: The EmonCMS instance full URL. Must end with "/".
        :param api_key: The EmonCMS instance's API key.
        """
        self.url = url
        self.api_key = api_key


class EmonCMSNode:
    """A class for doing all EmonCMS interactions"""

    def __init__(self, instance: EmonCMSInstance, node_name: str):
        """
        Initializes the EmonCMS instance.
        :param instance: The EmonCMS instance.
        :param node_name: The EmonCMS instance's node to publish to.
        """
        self.instance = instance
        self.node_name = node_name

    def send(self, output: dict) -> Response:
        """
        Sends a payload to the EmonCMS instance.
        :param output: The data to send, in a dict form.
        :return: The request's result.
        """
        output_json = json.dumps(output)
        url = self.instance.url
        key = self.instance.api_key
        return requests.get(
            f"{url}input/post?apikey={key}&node={self.node_name}&fulljson=" + output_json
        )
