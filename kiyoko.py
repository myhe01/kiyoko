import argparse
import json
import requests
import time
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
from inky.auto import auto
from zoneinfo import ZoneInfo

FONT_SIZE = 20
SCALE_SIZE = 1.30
DEV_PADDING = -5
X_START = 0
Y_START = 1
X_PADDING = 2
Y_PADDING = 4
URL_TO_GET = 'https://fdo.rocketlaunch.live/json/launches/next/5'
SLEEP_TIME = 30     # in seconds
TIMEOUT = 10        # in seconds

# Parse the launch data returned from the URL in JSON format
def parse_launch_data(x):
    list = []

    if x["t0"]:
        date = datetime.strptime(x["t0"], "%Y-%m-%dT%H:%MZ")
        list.append(True)
    else:
        temp_date = str(x["date_str"]) + " " + str(x["est_date"]["year"])
        date = datetime.strptime(temp_date, "%b %d %Y")
        list.append(False)

    utc = ZoneInfo('UTC')
    localtz = ZoneInfo('localtime')
    utctime = date.replace(tzinfo=utc)
    localtime = utctime.astimezone(localtz)

    list.append(localtime)
    list.append(x["name"])
    list.append(x["vehicle"]["name"])
    list.append(x["pad"]["name"])

    return list

def print_next_launch(list):
    print("Date: " + list[1].strftime("%B %d, %Y"))
    if list[0]:
        print("Time: " + list[1].strftime("%-I:%M %p"))
    print("Mission: " + str(list[2]))
    print("Vehicle: " + str(list[3]))
    print("Pad: " + str(list[4]))
    print("")

def update_display(inky_display, list):
    time = list[1].strftime("%-I:%M %p")
    date = list[1].strftime("%B %d, %Y")
    mission = str(list[2])
    vehicle = str(list[3])
    pad = str(list[4])

    time_w, time_h = helvetica_bold.getsize(time)
    time_x = X_START + X_PADDING
    time_y = Y_START + DEV_PADDING + 5
    draw.text((time_x, time_y), time, inky_display.BLACK, font=helvetica_bold)

    date_w, date_h = helvetica_bold.getsize(date)
    date_x = X_START + X_PADDING
    date_y = time_y + FONT_SIZE + Y_PADDING
    draw.text((date_x, date_y), date, inky_display.BLACK, font=helvetica_bold)

    mission_w, mission_h = helvetica_regular.getsize(mission)
    mission_x = X_START + X_PADDING
    mission_y = date_y + FONT_SIZE + Y_PADDING
    draw.text((mission_x, mission_y), mission, inky_display.BLACK, font=helvetica_regular)

    vehicle_w, vehicle_h = helvetica_regular.getsize(vehicle)
    vehicle_x = X_START + X_PADDING
    vehicle_y = mission_y + FONT_SIZE + Y_PADDING
    draw.text((vehicle_x, vehicle_y), vehicle, inky_display.BLACK, font=helvetica_regular)

    pad_w, pad_h = helvetica_regular.getsize(pad)
    pad_x = X_START + X_PADDING
    pad_y = vehicle_y + FONT_SIZE + Y_PADDING
    draw.text((pad_x, pad_y), pad, inky_display.BLACK, font=helvetica_regular)

    # Display the completed text
    inky_display.set_image(img)
    inky_display.show()

# Main
if __name__ == "__main__":
    # Init display
    try:
        inky_display = auto(ask_user=True, verbose=True)
    except TypeError:
        raise TypeError("You need to update the Inky library to >= v1.1.0")

    try:
        inky_display.set_border(inky_display.WHITE)
    except NotImplementedError:
        pass

    # Create a new canvas to draw on
    img = Image.new("P", inky_display.resolution)
    draw = ImageDraw.Draw(img)

    # Load the fonts
    helvetica_bold = ImageFont.truetype(r'fonts/helvetica-bold.ttf', int(FONT_SIZE * SCALE_SIZE))
    helvetica_regular = ImageFont.truetype(r'fonts/helvetica.ttf', int(FONT_SIZE * SCALE_SIZE))

    # Current and new launch data
    current_data = []
    new_data = []

    # Loop forever
    while True:
        # Get JSON from URL with a timeout of TIMEOUT
        current_result = requests.get(URL_TO_GET, timeout=TIMEOUT)

        # If response ok, then update our data
        if current_result.ok:
            launch_dict = json.loads(current_result.text)
            for x in launch_dict["result"]:
                if x["pad"]["location"]["state"] == 'FL':
                    new_data = parse_launch_data(x)
                    break

        if len(set(new_data).intersection(current_data)) != 5:
            print("New launch data!")
            current_data = new_data[:]
            update_display(inky_display, current_data)
            print_next_launch(current_data)
        else:
            print("No new launch data.")

        # Sleep for SLEEP_TIME
        time.sleep(SLEEP_TIME)


        