from requests.models import Response
import json
import requests


class EmonCMSNode:
    """A class for doing all EmonCMS interactions"""

    def __init__(self, instance, api_key, node_name):
        """
        Initializes the EmonCMS instance.

        :param instance: The EmonCMS instance full URL. Must end with "/".
        :param api_key: The EmonCMS instance's API key.
        :param node_name: The EmonCMS instance's node to publish to.
        """
        self.instance = instance
        self.api_key = api_key
        self.node_name = node_name

    def send(self, output: dict) -> Response:
        """
        Sends a payload to the EmonCMS instance.
        :param output: The data to send, in a dict form.
        :return: The request's result.
        """
        output_json = json.dumps(output)
        return requests.get(
            f"{self.instance}input/post?apikey={self.api_key}&node={self.node_name}&fulljson=" + output_json
        )
