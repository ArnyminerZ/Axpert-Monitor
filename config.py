import configparser
import os
import requests
from simplejson.errors import JSONDecodeError

config = configparser.ConfigParser()

CONFIG_FILE_NAME = "config.ini"


def load_configuration():
    is_config_valid = True
    if os.path.isfile(CONFIG_FILE_NAME):
        read = config.read(CONFIG_FILE_NAME)
        is_config_valid = len(read) > 0
    else:
        is_config_valid = False
    if not is_config_valid:
        # Configuration has to be made
        print("===========================")
        print("")
        print(" CONFIGURATION HELP WIZARD")
        print("")
        print("===========================")
        print("")

        print("Please, input your server's hostname.")
        print("This must be only the hostname or IP address, examples:")
        print("- example.com")
        print("- 81.126.59.185")
        hostname = None
        while not hostname:
            host = input("> ")
            if len(host) <= 0:
                print("Please, enter a valid hostname.")
            else:
                hostname = host
        print("")

        print("Please, input your server's port.")
        print("This must be a number, for example, the default http port is 80.")
        port = -1
        while port < 0:
            port_str = input("> ")
            if port_str.isdigit():
                port = int(port_str)
            else:
                print("Please, enter a valid port name.")
        print("")

        print("Please, input your server's path.")
        print("This is your EmonCMS's instance path, for example, you may access EmonCMS")
        print(" through http://example.com/emoncms/, then you should introduce emoncms/.")
        print("If your instance is at the root of the hostname, you can simply leave the")
        print(" field blank.")
        path = input("> ")
        if len(path) > 0 and not path.endswith("/"):
            path = path + "/"
        print("")

        print("Do you want to use https?")
        print("Type yes or no")
        protocol = None
        while protocol is None:
            https_str = input("> ")
            if https_str == "yes":
                protocol = 'https'
            elif https_str == "no":
                protocol = 'http'
            else:
                print("Please, type \"yes\" or \"no\".")
        print("")

        print("Please, enter your EmonCMS write-enabled API key. You can get it at:")
        print(f"{protocol}://{hostname}:{port}/input/api")
        api_key = None
        while not api_key:
            key = input("> ")
            if len(key) != 32:
                print("The API key is 32 characters long. Please check the input.")
            else:
                api_key = key
        print("")

        print("Checking key validity...", end="")
        addr = f"{protocol}://{hostname}:{port}/input/list/?apikey={api_key}"
        valid_request = requests.get(addr)
        valid_data = True
        if valid_request.status_code == 200:
            try:
                valid_request.json()
                print("ok")
            except JSONDecodeError:
                valid_data = False
        else:
            valid_data = False
        if not valid_data:
            print("error!")
            print("The introduced API key is not valid. This can be caused because you")
            print(" are not connected to the Internet, or simply because the API key is")
            print(" not valid. Type \"yes\" to continue.")
            shall_continue = input("> ")
            if shall_continue != "yes":
                exit()
        print("")

        print("Please, enter your desired node name. This can be almost anything, it's")
        print(" just an identifier for your device at EmonCMS.")
        node_name = None
        while not node_name:
            name = input("> ")
            if len(name) <= 0:
                print("Please, enter a valid name.")
            else:
                node_name = name
        print("")

        print("Configuration process complete, storing...")
        config['server'] = {}
        config['emoncms'] = {}
        config['server']['hostname'] = hostname
        config['server']['port'] = port
        config['server']['path'] = path
        config['server']['protocl'] = protocol
        config['emoncms']['apikey'] = api_key
        config['emoncms']['node_name'] = node_name
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            config.write(configfile)
        return load_configuration()
    else:
        return {
            "hostname": config['server']['hostname'],
            "port": config['server']['port'],
            "path": config['server']['path'],
            "https": config['server']['https'],
            "api_key": config['emoncms']['apikey'],
            "node_name": config['emoncms']['node_name'],
        }
