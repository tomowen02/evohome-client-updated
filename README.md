

# EvoPi
## Based on the _evohome-client_

![GitHub Logo](/images/evopi.png)

An Evohome browser based dashboard based on python. It can be run from any device capable of running Python scripts, but it was developed for a Raspberry Pi. The dash shows each of the user's devices, coloured according to their actual temperature vs their setpoint temperature. It is fully interactive, allowing the user to:

1. Set the temperature of all devices (zones and hot water)
2. Set the mode for the Evohome Controller (Auto, Economy, Away, Day Off, Custom, Off)
3. Backup and restore the user's schedule
4. Identifies which device is hotter/cooler than expected (device colour)
5. Displays which device is actively on (LED)
6. Shows the status of each device (Auto/Temporary Override)
7. Captures the Setpoint (target) temperature of each device
8. Shows when the device will change and the temperature it will change to (e.g. 22:00 > 16C) 


**EvoPi Instructions:**

From the terminal on the Raspeberry Pi run the following commands.

1. sudo mkdir EvoPi && cd EvoPi

2. sudo git clone https://github.com/clinkadink/evohome-client.git

3. cd evohome-client

4. Enter Honeywell API credentials in evoconfig.py

5. sudo python evopi.py

6. Open and navigate to http://localhost:9999 (or whichever IP you have configured)



Credits to @watchforstock, over at https://github.com/watchforstock and the _evohome-client_

--------------------------------------------------------------------------------------------------------------------------------------


Build status: [![CircleCI](https://circleci.com/gh/watchforstock/evohome-client.svg?style=svg)](https://circleci.com/gh/watchforstock/evohome-client)

Python client to access the [Total Connect Comfort](https://international.mytotalconnectcomfort.com/Account/Login) RESTful API.

It provides support for **Evohome** and the **Round Thermostat**.  It supports only EU/EMEA-based systems, please use [somecomfort](https://github.com/kk7ds/somecomfort) for US-based systems.

This client uses the [requests](https://pypi.org/project/requests/) library. If you prefer an async-friendly client, [evohome-async](https://github.com/zxdavb/evohome-async) has been ported to use [aiohttp](https://pypi.org/project/aiohttp/) instead.

Documentation (in progress) at http://evohome-client.readthedocs.org/en/latest/

Provides Evohome support for Home Assistant (and other automation platforms), see http://home-assistant.io/components/evohome/
