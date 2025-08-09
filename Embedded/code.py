from board import NEOPIXEL
from gc import collect
from time import sleep
from adafruit_matrixportal.matrixportal import MatrixPortal
from displayio import Group
from displayio import OnDiskBitmap
from displayio import TileGrid
from json import loads
from supervisor import reload

# -----------------------------------------------------
# INIT GLOBAL VARIABLES
# -----------------------------------------------------

# Get wifi details & environment variables from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Load variables from secrets.py config
api_url = secrets['mta_api_url']
station = secrets['mta_station']
direction = secrets['mta_train_direction']
lines = secrets.get('mta_train_lines', None)
debug = secrets['debug']

if lines:
    request_url = "http://{}/api/schedule/{}/{}/{}".format(api_url, station, lines, direction)
else:
    request_url = "http://{}/api/schedule/{}/{}".format(api_url, station, direction)

# Init HW
matrixportal = MatrixPortal(status_neopixel=NEOPIXEL, debug=debug, color_order="RBG")

# graphics buffer for sign bitmaps
sign_group = Group()

# Add sign graphics buffer
matrixportal.splash.append(sign_group)

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


# -----------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------

# Return info for a provided train schedule obj
def get_train_info(train_schedule):
    train_info = {}
    train_info['route'] = train_schedule['routeId']
    train_info['dep'] = train_schedule['relativeTime']
    train_info['dir'] = secrets['mta_train_direction']
    return train_info

# Return correct relative time string based on number length
def make_train_text(train_info):
    if train_info['dep'] >= 10:
        return "{} min".format(train_info['dep'])
    else:
        return " {} min".format(train_info['dep'])

# Clear sign graphics buffer
def clear_graphics():
    for i in range(len(sign_group)):
        sign_group.pop()

# Set a bitmap to graphics buffer
def display_bmp(buffer, bmp_path, pos_x, pos_y):
    try:
        bmp = OnDiskBitmap(bmp_path)
        tg = TileGrid(
            bmp,
            pixel_shader=bmp.pixel_shader,
            x=pos_x,
            y=pos_y
        )
        buffer.append(tg)
    except:
        raise Exception('Error loading {}'.format(bmp_path))

def get_bmp_for_route(train_info):
    return "gfx/{}.bmp".format(train_info['route'])

def get_exception_name(e):
    return str(e.__class__.__name__)

# -----------------------------------------------------
# MAIN PROGRAM LOOP
# -----------------------------------------------------

matrixportal.set_text("Connecting to: {}...".format(secrets['ssid']), 0)

lastruntime = None
started = False
try:
    while True:
        if not started:
            matrixportal.scroll_text(0.03)

        # get next train info
        try:
            schedule_response = matrixportal.fetch(request_url)
            schedule = loads(schedule_response)
            next_train_index = 0

            if not get_train_info( schedule[0] )['dep'] > 0:
                while get_train_info( schedule[0] )['dep'] < 0:
                    schedule.pop(0)
                    continue

            train1 = get_train_info( schedule[next_train_index] )
            train2 = get_train_info( schedule[next_train_index + 1] )
            collect()

            # clear Connecting text and stop initial check
            if not started:
                matrixportal.set_text("", 0)
                started = True

            # update graphics
            clear_graphics()
            display_bmp( sign_group, get_bmp_for_route(train1), 3, 0 )
            display_bmp( sign_group, get_bmp_for_route(train2), 3, 16 )
            collect()

            # update text
            matrixportal.set_text(make_train_text(train1), 1)
            matrixportal.set_text(make_train_text(train2), 2)
            collect()

        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

        except IndexError as e:
            matrixportal.set_text("No", 1)
            matrixportal.set_text("trains", 2)
            sleep(30)
            clear_graphics()
            continue

        sleep(30)

except Exception as e:
    exc = get_exception_name(e)
    error_text = "{}: restarting panel...".format(exc)
    print(error_text)
    print("{}: {}".format(exc, e))
    matrixportal.set_text(error_text, 0)
    matrixportal.scroll_text(0.03)
    reload()
