import board
import displayio
import json
import supervisor
import time
from adafruit_matrixportal.matrixportal import MatrixPortal

# Get wifi details & environment variables from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Init HW
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True, color_order="RBG")

# return info for a provided train schedule obj
def get_train_info(train_schedule):
    train_info = {}
    train_info['route'] = train_schedule['routeId']
    train_info['dep'] = train_schedule['relativeTime']
    train_info['dir'] = secrets['mta_train_direction']
    return train_info

# return correct relative time string based on number length
def make_train_text(train_info):
    if train_info['dep'] >= 10:
        return "{} min".format(train_info['dep'])
    else:
        return " {} min".format(train_info['dep'])

def display_bmp(bmp_path, pos_x, pos_y):
    try:
        bmp = displayio.OnDiskBitmap(bmp_path)
        tg = displayio.TileGrid(
            bmp,
            pixel_shader=bmp.pixel_shader,
            x=pos_x,
            y=pos_y
        )
        matrixportal.splash.append(tg)
    except:
        raise Exception('Error loading {}'.format(bmp_path))

def get_bmp_for_route(train_info):
    return "gfx/{}.bmp".format(train_info['route'])

# -----------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------

# load variables from secrets.py config
api_url = secrets['mta_api_url']
station = secrets['mta_station']
direction = secrets['mta_train_direction']
request_url = "http://{}/api/schedule/{}/{}".format(api_url, station, direction)

# Set up text labels for dynamic display
# Connecting text (id: 0)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(0, (matrixportal.graphics.display.height // 2) - 1),
    scrolling=True
)

# train1 time (id: 1)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(24, int(matrixportal.graphics.display.height * 0.25) - 1),
    scrolling=False,
)

# train2 time (id: 2)
matrixportal.add_text(
    text_color=0xFFFFFF,
    text_position=(24, int(matrixportal.graphics.display.height * 0.75) - 1),
    scrolling=False,
)

matrixportal.set_text("Connecting to: {}...".format(secrets['ssid']), 0)

localtime_refresh = None
started = False
try:
    while True:
        if not started:
            matrixportal.scroll_text(0.03)
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
                display_bmp( get_bmp_for_route(train1), 3, 0 )
                display_bmp( get_bmp_for_route(train2), 3, 16 )

                # update text
                matrixportal.set_text(make_train_text(train1), 1)
                matrixportal.set_text(make_train_text(train2), 2)

            except RuntimeError as e:
                print("Some error occured, retrying! -", e)
                continue
except Exception as e:
    error_text = "Error: restarting panel..."
    print(error_text, e)
    matrixportal.set_text(error_text, 0)
    matrixportal.scroll_text(0.03)
    supervisor.reload()
