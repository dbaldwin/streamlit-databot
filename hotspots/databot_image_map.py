from typing import Tuple

databot_image_map = {
    1: {
        "name": "Accelerometer",
        "sensor_name": "accl",
        "desc": "The accelerometer senses motion and it is one of the most widely used sensors in the world.\nThe accelerometer is in a module called an inertial measurement unit (IMU).",
        "databot_tutorial_url": "https://databot.us.com/starters-acc/"
    },
    2: {
        "name": "Air Pressure",
        "sensor_name": "pressure",
        "desc": "The air pressure sensor measures atmospheric pressure also called barometric pressure.",
        "databot_tutorial_url": "https://databot.us.com/ss-pressure/"

    }
}


def find_image_map_entry(sensor_name: str) -> Tuple[int,dict] :
    for key, value in databot_image_map.items():
        if value['sensor_name'] == sensor_name:
            return key, value
    else:
        return -1, {}
