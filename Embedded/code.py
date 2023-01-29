import time
import board
import json
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
    train_info['route'] = train_schedule['routeId']
    train_info['dep'] = train_schedule['relativeTime']
    train_info['dir'] = secrets['mta_train_direction']
    return train_info

def make_train_text(train_info):
    if train_info['dep'] >= 10:
        return "{} min".format(train_info['dep'])
    else:
        return " {} min".format(train_info['dep'])

api_url = secrets['mta_api_url']
station = secrets['mta_station']
direction = secrets['mta_train_direction']
request_url = "http://{}/api/schedule/{}/{}".format(api_url, station, direction)

# Connecting text (id: 0)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(0, (matrixportal.graphics.display.height // 2) - 1),
    scrolling=True
)

# train1 time (id: 1)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(22, int(matrixportal.graphics.display.height * 0.25) - 2),
    scrolling=False,
)

# train2 time (id: 2)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(22, int(matrixportal.graphics.display.height * 0.75)),
    scrolling=False,
)

# train1 sign (id: 3)
matrixportal.add_text(
    text_color=0x000000,
    text_position=(7, 7),
    scrolling=False,
)

# train2 sign (id: 4)
matrixportal.add_text(
    text_color=0x000000,
    text_position=(7, 23),
    scrolling=False,
)

matrixportal.set_text("Connecting to Wi-Fi network...", 0)

localtime_refresh = None
started = False
while True:
    if not started:
        matrixportal.scroll_text(0.04)
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
            schedule = json.loads(schedule_response)
            next_train_index = 0

            if not get_train_info( schedule[0] )['dep'] > 0:
                next_train_index = 1

            train1 = get_train_info( schedule[next_train_index] )
            train2 = get_train_info( schedule[next_train_index + 1] )

            # clear Connecting text and stop initial check
            matrixportal.set_text(" ", 0)
            started = True
            
            # update graphics
            matrixportal.set_background("gfx/routes.bmp")
            matrixportal.set_text(make_train_text(train1), 1)
            matrixportal.set_text(train1['route'], 3)
            matrixportal.set_text(make_train_text(train2), 2)
            matrixportal.set_text(train2['route'], 4)

        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue
