import time
import board
import json
import math
from adafruit_datetime import datetime
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.matrixportal import MatrixPortal

# Get wifi details & environment variables from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

matrix = Matrix()

# Init HW
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)

# return info for a provided train schedule obj
def get_train_info(train_schedule):
    train_info = {}
    current_time = time.time() #timestamp
    mins_to_departure = math.floor((train_schedule['departureTime'] - current_time) / 60) - 300

    train_info['route'] = train_schedule['routeId']
    train_info['dep'] = mins_to_departure
    train_info['dir'] = secrets['mta_train_direction']

    return train_info

def make_arrival_text(train_info):
    if train_info['dep'] >= 10:
        return " {}  {} min".format(train_info['route'], train_info['dep'])
    else:
        return " {}   {} min".format(train_info['route'], train_info['dep'])

api_url = secrets['mta_api_url']
station = secrets['mta_station']
direction = secrets['mta_train_direction']
request_url = "http://{}/api/schedule/{}".format(api_url, station)
# debug
# print("req: {}".format(request_url))

matrixportal.add_text(
    text_position=(0, int(matrixportal.graphics.display.height * 0.25) - 2),
    scrolling=False,
)

matrixportal.add_text(
    text_position=(0, int(matrixportal.graphics.display.height * 0.75)),
    scrolling=False,
)

localtime_refresh = None
while True:
    # query once every 30s (and on first run)
    if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 30:
        try:
            print("Getting time from internet!")
            matrixportal.get_local_time()
            localtime_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue
    
        # get next train info
        try:
            # print("fetching from API...")
            schedule_response = matrixportal.fetch(request_url)
            schedule_south = json.loads(schedule_response)[direction]
            next_train_index = 0

            if not get_train_info( schedule_south[0] )['dep'] > 0:
                next_train_index = 1

            train1 = get_train_info( schedule_south[next_train_index] )
            train2 = get_train_info( schedule_south[next_train_index + 1] )

            # debug
            # print("Next train: {}, direction: {}, leaving in: {}".format(train1['route'], train1['dir'], train1['dep']))
            # print("Next train: {}, direction: {}, leaving in: {}".format(train2['route'], train2['dir'], train2['dep']))

            matrixportal.set_text(make_arrival_text(train1), 0)
            matrixportal.set_text(make_arrival_text(train2), 1)

        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    