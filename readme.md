# MTA Train Sign built with Raspberry Pi + LED Matrix


* An Express.js server which parses current train data from mta-gtfs and provides an API for easy display of data
* A CircuitPython app to handle display of selected NYC subway station data on a 64x32 LED Matrix via the Adafruit Matrix Portal microcontroller.


## Requirements
* MTA API Key
  * https://datamine.mta.info/
* Adafruit [Matrix Portal](https://learn.adafruit.com/adafruit-matrixportal-m4)
  * https://www.adafruit.com/product/4745
* 5V 4A power supply (to power LED matrix + portal)
  * https://www.adafruit.com/product/1466
* 5V Power Cable
  * In case the LED matrix didn't come with it, pick this up too
  * https://www.adafruit.com/product/4767 
* 64x32 LED RGB Matrix
  * Example: https://www.adafruit.com/product/2277
  * Any 64x32 panel works as long as it's compatible with the HUB75 standard

&nbsp;
![Front of 64x32 RGB LED Matrix display](https://i.imgur.com/ylAQq8a.png)

# Hardware
### Adafruit Matrix Portal
Install the Matrix Portal directly onto the LED Matrix using the 16-pin HUB75 connector. Make sure that you install it with the Portal's USB-C connector facing outwards, and with the Matrix's arrows printed on the rear side pointing **up** and **right** (orientation matters).

### RGB LED Matrix
It might even come with multiple data cables in the event that you want to bridge dipslays. The data cable will plug directly into the back of the display and your Bonnet/HAT. The power cable will also plugin into the back of the display and two pronged ends will connect to slotted terminals with screws on the Bonnet/HAT.

### Power cable
Connect the forked ends of the power cable to the screw standoffs on the Matrix Portal, using the included screws. Attach the other end to the 4-pin power connector (make sure to connect the right side for 5V & ground).

![Backside of display with Raspberry Pi & RGB Matrix HAT](https://cdn-learn.adafruit.com/assets/assets/000/095/023/original/led_matrices_4745-12.jpg?1600966452)

# Software
This project is split in two parts: 
1. The **API** (`Server/`) which connects to the MTA's API, and offers an endpoint for the Matrix to retrieve data from over your local Wi-Fi network.
2. The **CircuitPython code** for the Matrix Portal (`Embedded/`), which connects to your local Wi-Fi network, queries the API server, and displays upcoming departures for a given MTA subway station.

## Dependencies

### API server

* Node.js LTS & npm installed on the computer or server which will host the API
* (optional) [Forever.js](https://www.npmjs.com/package/forever) installed globally
  * `sudo npm install forever -g`
  * Allows the API server to run continuously

### Matrix Portal

* [CircuitPython](https://learn.adafruit.com/adafruit-matrixportal-m4/install-circuitpython) (see "Install CircuitPython" section)
* [Adafruit libraries](https://learn.adafruit.com/adafruit-matrixportal-m4/circuitpython-setup) for CircuitPython. The below are needed for this project:
  * adafruit_matrixportal
  * adafruit_portalbase
  * adafruit_esp32spi
  * neopixel.mpy
  * adafruit_bus_device
  * adafruit_requests.mpy
  * adafruit_fakerequests.mpy
  * adafruit_io
  * adafruit_bitmap_font
  * adafruit_display_text
  * adafruit_minimqtt
  * adafruit_datetime

## Getting Started
1. Sign up for an account and generate an API key from the MTA Real-Time Data Feeds website: https://api.mta.info
2. Set up any dependencies on the host machine you'll use for the API. A raspberry pi at home works great, or you could also set up on a cloud VPS or managed service that can run node.js.

## Installing
Install dependencies:

```bash
# For the API server
$ cd nyc-train-sign/Server/node
$ npm install
```

## Configuration

### 1. Configure and test the Server application
In `Server/node`, create a file called `.env` and supply the below info:

`API_KEY`: Your MTA access token  
`FEED_ID`: The ID of the feed to check for train routes. This should be one of the following based on your local station:

```json
{
  '123456': undefined,
  'ACE': '-ace',
  'BDFM': '-bdfm',
  'G': '-g',
  'JZ': '-jz',
  'NQRW': '-nqrw',
  'L': '-l',
  '7': '-7',
  'SIR': '-si'
}
```

Example `.env`:
```bash
API_KEY=<YOUR_MTA_API_KEY>
FEED_ID=-nqrw
```

After configuring the Server applicaton, you should test it by running it manually. This will be necessary as you will need to access the API in order to find your `stationId` which will be required to configure the UI application.

```bash
# Run the server manually
$ cd nyc-train-sign/Server/node
$ sudo node app.js
  > Node.js server listening on 8080
```

Get the list of subway stations and find yours. Make note/write down of the `stop_id` associated to your subway station:
```bash
# In an internet browser, go to the below address, or curl from a console:
# From your Raspbery Pi:
$ curl localhost:8080/api/station

# From a computer on the same wifi network as the Raspberry Pi
$ curl http://raspberrypi.local:8080/api/station
```


### 2. Configure and test the UI application
Update the UI configuration file. Use your subway station's `stop_id` you wrote down for the `mta_station`. Supply a direction, "N", or "S", and the IP + Port or domain name of your API server from step 1:
```Python
# Update your secrets.py with Wi-Fi info & subway preferences, ex:
secrets = {
    'ssid' : '<YOUR_WIFI_SSID>',
    'password' : '<YOUR_WIFI_PASSWORD>',
    
    # http://worldtimeapi.org/timezones
    'timezone' : "America/New_York", 
    
    # find this ID from your API endpoint: 
    # localhost:8080/api/station
    'mta_station': 'R03', 
    
    # either N or S
    'mta_train_direction': 'S', 
    
    # update this to the IP:Port or host domain 
    # that is running your API server
    'mta_api_url': '192.168.86.32:8080'
}
```

After you have flashed your Matrix Portal with CircuitPython, connect it to your computer via USB and copy over all the files inside the `Embedded/` folder to its root directory.

# REST API

The REST API for the server appliation is described below. Data formatted and parsed from [mta-gtfs](https://github.com/aamaliaa/mta-gtfs), an NYC MTA API library.

## Get MTA subway service status info

### Request

`GET /api/status/`

### Response

```json
[
  {
    "name": "123",
    "status": "GOOD SERVICE",
    "text": "",
    "Date": "",
    "Time": ""
  },
  {
    "name": "456",
    "status": "DELAYS",
    "text": "<span class=\"TitleDelay\">Delays</span>
            <span class=\"DateStyle\">
            &nbsp;Posted:&nbsp;08/16/2019&nbsp; 6:06PM
            </span><br/><br/>
            Northbound [4], [5] and [6] trains are delayed while crews work to correct signal problems at <b>59 St.</b>
            <br/><br/>",
    "Date": "08/16/2019",
    "Time": " 6:06PM"
  },
]
```


## Get MTA subway service status info for specific subway train name

### Request

`GET /api/status/:trainName/`

  * GET /api/status/3/

### Response

```json
[
  {
    "name": "123",
    "status": "GOOD SERVICE",
    "text": "",
    "Date": "",
    "Time": ""
  }
]
```


## Get a list of all subway stations

### Request

`GET /api/station/`

### Response

```json
{
  "101": {
    "stop_id": "101",
    "stop_code": "",
    "stop_name": "Van Cortlandt Park - 242 St",
    "stop_desc": "",
    "stop_lat": "40.889248",
    "stop_lon": "-73.898583",
    "zone_id": "",
    "stop_url": "",
    "location_type": "1",
    "parent_station": ""
  },
  "103": {
    "stop_id": "103",
    "stop_code": "",
    "stop_name": "238 St",
    "stop_desc": "",
    "stop_lat": "40.884667",
    "stop_lon": "-73.90087",
    "zone_id": "",
    "stop_url": "",
    "location_type": "1",
    "parent_station": ""
  },
}
```


## Get a single subway station's metadata

### Request

`GET /api/station/:stationId/`

  * GET /api/station/249/

### Response

```json
{
  "stop_id": "249",
  "stop_code": "",
  "stop_name": "Kingston Av",
  "stop_desc": "",
  "stop_lat": "40.669399",
  "stop_lon": "-73.942161",
  "zone_id": "",
  "stop_url": "",
  "location_type": "1",
  "parent_station": ""
}
```

## Get the current schedule of trains at a specific station

### Request

`GET /api/schedule/:stationId/`

  * GET /api/schedule/249/

### Response

```json
{
  "N": [
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1565958549,
      "departureTime": 1565958549
    },
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1566000654,
      "departureTime": 1566000654
    },
  ],
  "S": [
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1566000745,
      "departureTime": 1566000745
    },
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1566001280,
      "departureTime": 1566001280
    },
  ]
}
```

## Get the current schedule of a specific train at a specific station

### Request

`GET /api/schedule/:stationId/:trainName/:direction/`

  * GET /api/schedule/249/3/N/

### Response

```json
{
  "N": [
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1565958549,
      "departureTime": 1565958549
    },
    {
      "routeId": "3",
      "delay": null,
      "arrivalTime": 1566000654,
      "departureTime": 1566000654
    },
  ]
}
```