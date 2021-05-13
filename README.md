# Axpert Monitor
A Python script that aims to offer wireless monitoring for Axpert Inverters. Currently supports EmonCMS (mandatory) and MQTT.

Prepared to work on RPi, may not work on other systems.

# Installation
## Requirements
Update system:
```shell
sudo apt update -y && sudo apt upgrade -y
```
Git:
```shell
sudo apt install git
```
Python 3:
```shell
sudo apt install python3
sudo python3 -m ensurepip
```
Python packages:
```shell
pip install serial crcmod paho-mqtt
```

## Download
```shell
git clone https://github.com/ArnyminerZ/Axpert-Monitor.git
```

## Run
```shell
cd Axpert-Monitor
python3 .
```

## Initial Configuration
In the first launch you will be greeted with a configuration wizard, follow the steps indicated, and you will be ready to go.
