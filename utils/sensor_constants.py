from pathlib import Path

DATABOT_DATA_FILE = Path("./data/databot_data.json").absolute()
DATABOT_IMAGE_PATH = Path("./hotspots/databot.png").absolute()
DATABOT_HOTSPOTS_DATA = Path("./hotspots/databot-hotspots.csv").absolute()

magneto_description = """The "magneto" is shorthand term for a "magnetometer," which is one of the sensors on the Databot2.0 device. A magnetometer is an instrument used to measure the strength and direction of magnetic fields. It can detect the presence of nearby magnetic objects or magnetic fields and is commonly used in various applications, such as navigation, geophysics, robotics, and consumer electronics.

In the context of Databot2.0, the magnetometer may be used to gather data on magnetic fields in the surrounding environment, which could be valuable for various purposes like detecting the Earth's magnetic field, orienting the device with respect to magnetic north, or identifying magnetic objects in the vicinity. The data from the magnetometer can be integrated with other sensor data to provide a comprehensive understanding of the device's surroundings and its orientation."""

ldist_description = """
Hey there! So, the Databot2.0 is a cool device with lots of sensors on it. One of these sensors is called the "Ldist" sensor. Ldist stands for "Laser Distance" sensor, and it does exactly what its name suggests – it measures distances using laser technology.

Imagine you have a tiny laser pointer on the Databot2.0, and it shoots out a tiny, invisible laser beam like you see in some cool spy movies! Now, when this laser beam hits an object, it bounces back to the Databot2.0. The Ldist sensor then quickly calculates how long it took for the laser beam to go out and come back, and it uses that time to figure out how far the object is from the Databot2.0.

Let's say the Databot2.0 is looking at a wall that is 2 meters away. The Ldist sensor will read a value of "2 meters." If the Databot2.0 moves closer to the wall, the Ldist sensor will read a smaller value, like "1.5 meters." And if it moves farther away from the wall, the sensor will read a larger value, like "3 meters."

In summary, the Ldist sensor on the Databot2.0 is like a magical laser ruler that helps the device know how far away things are from it. It's super useful for the Databot2.0 to understand its surroundings and interact with the world!
"""
databot_sensors = {
    'accl': {
        'sensor_name': 'accl',
        'friendly_name': 'Acceleration',
        'save': False,
        'display': False,
        'data_columns': ['acceleration_x', 'acceleration_y', 'acceleration_z', 'absolute_acceleration']
    },
    'Laccl': {
        'sensor_name': 'Laccl',
        'friendly_name': 'Linear Acceleration',
        'save': False,
        'display': False,
        'data_columns': ['linear_acceleration_x', 'linear_acceleration_y', 'linear_acceleration_z',
                         'absolute_linear_acceleration']
    },
    'gyro': {
        'sensor_name': 'gyro',
        'friendly_name': 'Gyroscope',
        'save': False,
        'display': False,
        'data_columns': ['gyro_x', 'gyro_y', 'gyro_z']
    },
    'magneto': {
        'sensor_name': 'magneto',
        'friendly_name': 'Magneto',
        'save': False,
        'display': False,
        'description': magneto_description,
        'data_columns': ['mag_x', 'mag_y', 'mag_z']

    },
    # 'IMUTemp': {
    #     'sensor_name': 'IMUTemp',
    #     'friendly_name': 'IMU Temperature',
    #     'save': False,
    #     'display': False
    # },
    'Etemp1': {
        'sensor_name': 'Etemp1',
        'friendly_name': 'External Temperature 1',
        'save': False,
        'display': False,
        'data_columns': ['external_temp_1']
    },
    'Etemp2': {
        'sensor_name': 'Etemp2',
        'friendly_name': 'External Temperature 2',
        'save': False,
        'display': False,
        'data_columns': ['external_temp_2']
    },
    'pressure': {
        'sensor_name': 'pressure',
        'friendly_name': 'Atmospheric Pressure',
        'save': False,
        'display': False,
        'data_columns': ['pressure']
    },
    'alti': {
        'sensor_name': 'alti',
        'friendly_name': 'Altimeter',
        'save': False,
        'display': False,
        'data_columns': ['altitude']
    },
    'ambLight': {
        'sensor_name': 'ambLight',
        'friendly_name': 'Ambient Light',
        'save': False,
        'display': False,
        'data_columns': ['ambient_light_in_lux']
    },
    # 'rgbLight': {
    #     'sensor_name': 'rgbLight',
    #     'friendly_name': 'RGB Light',
    #     'save': False,
    #     'display': False,
    #     'data_columns': ['r_light', 'g_light', 'b_light']
    # },
    'UV': {
        'sensor_name': 'UV',
        'friendly_name': 'UltraViolet Light',
        'save': False,
        'display': False,
        'data_columns': ['uv_index']
    },
    'co2': {
        'sensor_name': 'co2',
        'friendly_name': 'CO2',
        'save': False,
        'display': False,
        'data_columns': ['co2']
    },
    'voc': {
        'sensor_name': 'voc',
        'friendly_name': 'Volatile Organic Compound',
        'save': False,
        'display': False,
        'data_columns': ['voc']
    },
    'hum': {
        'sensor_name': 'hum',
        'friendly_name': 'Humidity',
        'save': False,
        'display': False,
        'data_columns': ['humidity']
    },
    # 'humTemp': {
    #     'sensor_name': 'humTemp',
    #     'friendly_name': 'Humidity Adjusted Temperature',
    #     'save': False,
    #     'display': False,
    #     'data_columns': ['humidity_temperature']
    # },
    # 'Sdist': {
    #     'sensor_name': 'Sdist',
    #     'friendly_name': 'Short Distance',
    #     'save': False,
    #     'display': False,
    #     'data_columns': ['distance']
    # },
    'noise': {
        'sensor_name': 'noise',
        'friendly_name': 'Noise',
        'save': False,
        'display': False,
        'data_columns': ['noise_sound']
    },
    'Ldist': {
        'sensor_name': 'Ldist',
        'friendly_name': 'Laser Distance',
        'save': False,
        'display': False,
        'data_columns': ['distance']

    },
    'gesture': {
        'sensor_name': 'gesture',
        'friendly_name': 'Gesture',
        'save': False,
        'display': False,
        'data_columns': ['gesture']
    },

}
