import json
import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo

URL_TO_GET = 'https://fdo.rocketlaunch.live/json/launches/next/5'
SLEEP_TIME = 60     # in seconds
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
    print_next_launch(list)

def print_next_launch(list):
    print("Date: " + list[1].strftime("%B %d, %Y"))
    if list[0]:
        print("Time: " + list[1].strftime("%X"))
    print("Mission: " + str(list[2]))
    print("Vehicle: " + str(list[3]))
    print("Pad: " + str(list[4]))
    print("")

# Main
if __name__ == "__main__":
    # Loop forever
    while True:
        # Get JSON from URL with a timeout of TIMEOUT
        current_result = requests.get(URL_TO_GET, timeout=TIMEOUT)

        # If response ok, then update our data
        if current_result.ok:
            launch_dict = json.loads(current_result.text)
            for x in launch_dict["result"]:
                if x["pad"]["location"]["state"] == 'FL':
                    parse_launch_data(x)
                    break

        # Sleep for SLEEP_TIME
        time.sleep(SLEEP_TIME)


        