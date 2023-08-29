import platform

import streamlit as st
from databot.PyDatabot import PyDatabot, DefaultDatabotConfig, DatabotConfig
import dataclasses
import cv2
from streamlit_image_coordinates import streamlit_image_coordinates
import pandas as pd
import subprocess
from pathlib import Path
import pickle
import time
import altair as alt

st.set_page_config(
    page_title="Databot Dashboard",
    page_icon="✅",
    layout="wide",
)

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
        'friendly_name': 'Acceleration',
        'save': False,
        'display': False,
        'data_columns': ['acceleration_x', 'acceleration_y', 'acceleration_z']
    },
    'Laccl': {
        'friendly_name': 'Linear Acceleration',
        'save': False,
        'display': False,
        'data_columns': ['linear_acceleration_x', 'linear_acceleration_y', 'linear_acceleration_z', 'absolute_linear_acceleration']
    },
    'gyro': {
        'friendly_name': 'Gyroscope',
        'save': False,
        'display': False,
        'data_columns': ['gyro_x', 'gyro_y', 'gyro_z']
    },
    'magneto': {
        'friendly_name': 'Magneto',
        'save': False,
        'display': False,
        'description': magneto_description,
        'data_columns': ['mag_x', 'mag_y', 'mag_z']

    },
    'IMUTemp': {
        'friendly_name': 'IMU Temperature',
        'save': False,
        'display': False
    },
    'Etemp1': {
        'friendly_name': 'External Temperature 1',
        'save': False,
        'display': False
    },
    'Etemp2': {
        'friendly_name': 'External Temperature 2',
        'save': False,
        'display': False
    },
    'pressure': {
        'friendly_name': 'Atmospheric Pressure',
        'save': False,
        'display': False,
        'data_columns': ['pressure']
    },
    'alti': {
        'friendly_name': 'Altimeter',
        'save': False,
        'display': False,
        'data_columns': ['altitude']
    },
    'ambLight': {
        'friendly_name': 'Ambient Light',
        'save': False,
        'display': False,
        'data_columns': ['ambient_light_in_lux']
    },
    'rgbLight': {
        'friendly_name': 'RGB Light',
        'save': False,
        'display': False,
        'data_columns': ['r_light', 'g_light', 'b_light']
    },
    'UV': {
        'friendly_name': 'UltraViolet Light',
        'save': False,
        'display': False,
        'data_columns': ['uv_index']
    },
    'co2': {
        'friendly_name': 'CO2',
        'save': False,
        'display': False,
        'data_columns': ['co2']
    },
    'voc': {
        'friendly_name': 'Volatile Organic Compound',
        'save': False,
        'display': False,
        'data_columns': ['voc']
    },
    'hum': {
        'friendly_name': 'Humidity',
        'save': False,
        'display': False,
        'data_columns': ['humidity']
    },
    'humTemp': {
        'friendly_name': 'Humidity Adjusted Temperature',
        'save': False,
        'display': False,
        'data_columns': ['humidity_temperature']
    },
    'Sdist': {
        'friendly_name': 'Short Distance',
        'save': False,
        'display': False
    },
    'noise': {
        'friendly_name': 'Noise',
        'save': False,
        'display': False
    },
    'Ldist': {
        'friendly_name': 'Long Distance',
        'save': False,
        'display': False
    },
    'gesture': {
        'friendly_name': 'Gesture',
        'save': False,
        'display': False
    },

}

def read_databot_data_file() -> pd.DataFrame:
    try:
        df = pd.read_json(path_or_buf="./data/test_data.txt", lines=True)
        df.sort_values(by=['time'], ascending=False, inplace=True)
        return df
    except:
        return None

def is_point_in_box(x1, y1, x2, y2, x, y):
    return (x1 <= x <= x2) and (y1 <= y <= y2)


def find_box(normal_x: float, normal_y: float, df: pd.DataFrame):
    for row in df.iterrows():
        if is_point_in_box(row[1]['upper_left_x'], row[1]['upper_left_y'], row[1]['lower_right_x'],
                           row[1]['lower_right_y'], normal_x, normal_y):
            return row
    else:
        return None


@st.cache_data
def read_hot_spots(csv_filepath: str) -> pd.DataFrame:
    df = pd.read_csv(csv_filepath)
    return df


@st.cache_data
def read_image(image_path: str):
    _image = cv2.imread(image_path)
    im_rgb = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
    # _image = imutils.resize(_image, width, height)
    return im_rgb

# def _databot_sensor_file_on_change(*args, **kwargs):
#     print(args)
#     key = args[0].split("_")[0]
#     databot_sensors[key]['save'] = st.session_state[args[0]]
#
# def _databot_sensor_display_on_change(*args, **kwargs):
#     print(args)
#     key = args[0].split("_")[0]
#     databot_sensors[key]['display'] = st.session_state[args[0]]

def setup_input_selection_sidebar():
    with st.sidebar:
        st.header("Databot Sensors")
        fields = dataclasses.fields(DefaultDatabotConfig)
        field_names = []
        for field in fields:
            field_names.append(field.name)
        # field_names = sorted(field_names)

        for field_name in field_names:
            if field_name in databot_sensors:
                databot_sensor = databot_sensors[field_name]
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(databot_sensor['friendly_name'])
                with col2:
                    st.checkbox("SaveToFile", value=databot_sensor['save'],  key=f"{field_name}_save_cb")
                with col3:
                    st.checkbox("Display", value=databot_sensor['display'], key=f"{field_name}_display_cb")


def create_databot_config() -> DatabotConfig:
    databot_config = DatabotConfig()
    fields = dataclasses.fields(DefaultDatabotConfig)
    for field in fields:
        checkbox_key = f"{field.name}_save_cb"
        if checkbox_key in list(st.session_state.keys()):
            if st.session_state[checkbox_key]:
                setattr(databot_config, field.name, True)
    return databot_config

def collect_data_on_click():
    if 'pydatabot_process' not in st.session_state:
        # remove datafile
        if Path("./data/test_data.txt").exists():
            Path("./data/test_data.txt").unlink()
        databot_config: DatabotConfig = create_databot_config()
        with open("streamlit_databot_config.pkl", "wb") as f:
            pickle.dump(databot_config, f)
        # windows needs shell=True, macos shell=False
        if "windows" in platform.system().lower():
            shell_flag = True
        else:
            shell_flag = False
        st.session_state.pydatabot_process = subprocess.Popen(["python", "pydatabot_save_data_to_file.py"], cwd=Path(".").absolute(), shell=shell_flag)


def stop_collecting_data_on_click():
    if 'pydatabot_process' in st.session_state:
        st.session_state.pydatabot_process.terminate()
        del st.session_state['pydatabot_process']


def draw_dashboard(placeholder_component, refresh_rate: int = 1):
    with placeholder_component.container():
        df = read_databot_data_file()
        if df is not None:
            st.write(f":cyan[Number of records read: {df.shape[0]}]")

            # if the pydata is processing/collecting data
            # then check to see if we should stop collecting
            if 'pydatabot_process' in st.session_state:
                number_of_samples_to_collect = st.session_state['number_of_samples_to_collect']
                if number_of_samples_to_collect > 0 and df.shape[0] >= number_of_samples_to_collect:
                    stop_collecting_data_on_click()
                    return

            st.dataframe(df, use_container_width=True)
            fields = dataclasses.fields(DefaultDatabotConfig)
            for field in fields:
                checkbox_key = f"{field.name}_display_cb"
                if checkbox_key in list(st.session_state.keys()):
                    if st.session_state[checkbox_key]:
                        data_columns = databot_sensors[field.name]['data_columns']
                        if len(data_columns) == 1:
                            number_of_samples_to_display = st.session_state['number_of_samples_to_display']
                            if number_of_samples_to_display > 0:
                                df = df.head(number_of_samples_to_display)
                            # st.line_chart(df, x="time", y=data_column, use_container_width=True)
                            try:
                                st.divider()
                                st.write(databot_sensors[field.name]['friendly_name'])
                                c = alt.Chart(df).mark_line().encode(x='time', y=data_columns[0])
                                st.altair_chart(c, use_container_width=True)
                            except:
                                pass
                        else:
                            # make multi-line line chart in altair.... which is a little weird for the data
                            # https://altair-viz.github.io/user_guide/data.html#long-form-vs-wide-form-data

                            # df_cols are the columns we expect from collecting data
                            df_cols = data_columns.copy()
                            df_cols.append("time")
                            try:
                                # it is possible that the new selection and the existing data have
                                # different columns...
                                df_sensor_values = df[df_cols]
                                # print(df_sensor_values.columns)
                                number_of_samples_to_display = st.session_state['number_of_samples_to_display']
                                if number_of_samples_to_display > 0:
                                    df_sensor_values = df_sensor_values.head(number_of_samples_to_display)

                                st.divider()
                                st.write(databot_sensors[field.name]['friendly_name'])
                                c = alt.Chart(df_sensor_values).transform_fold(
                                    databot_sensors[field.name]['data_columns'],
                                    as_=['sensor_name', 'sensor_value']
                                ).mark_line().encode(x='time:T', y='sensor_value:Q', color='sensor_name:N')
                                st.altair_chart(c, use_container_width=True)
                            except:
                                pass

    if refresh_rate > 0:
        time.sleep(refresh_rate)


def main():
    st.header("DroneBlocks databot2.0 Dashboard")
    setup_input_selection_sidebar()
    tab1, tab2 = st.tabs(["Dashboard", "Sensor Map"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        st.divider()
        with col1:
            st.button("Collect Data", key='collect_data', on_click=collect_data_on_click)
        with col2:
            st.button("Stop Collecting data", key="stop_collect_data", on_click=stop_collecting_data_on_click)
        with col3:
            st.checkbox(label="Data refresh", value=False, key="data_refresh")


        col4, col5 = st.columns(2)
        with col4:
            st.write("Display the last 'n' number of data samples.")
            st.write("Set to zero for all data values")
        with col5:
            st.number_input(label="Number of samples to display", min_value=0, max_value=300, value=0, step=1, key="number_of_samples_to_display")

        st.divider()
        col6, col7 = st.columns(2)
        with col6:
            st.write("Total number of samples to collect")
            st.write("Set to zero to not limit the number of datapoints")
        with col7:
            st.number_input(label="Number of samples to collect", min_value=0, max_value=5000, value=0, step=1, key="number_of_samples_to_collect")

        st.divider()

        placeholder = st.empty()

        while 'data_refresh' in st.session_state and st.session_state['data_refresh']:
            if 'pydatabot_process' in st.session_state:
                draw_dashboard(placeholder)
            else:
                break

        draw_dashboard(placeholder, refresh_rate=0)


    with tab2:
        st.write("Sensor Map")
        hotspots_df = read_hot_spots("./hotspots/databot-hotspots.csv")
        st.dataframe(hotspots_df)
        st.write(hotspots_df.shape)
        the_image = read_image("./hotspots/databot.png")
        # st.image(image=the_image)

        value = streamlit_image_coordinates(source=the_image, height=650, width=650, key="db_image")
        #
        st.write(value)
        if value is not None:
            normal_x = value['x'] / the_image.shape[1]
            normal_y = value['y'] / the_image.shape[0]
            st.write(f"({normal_x},{normal_y})")
            box = find_box(normal_x, normal_y, hotspots_df)
            if box is not None:
                print(f"Index: {box[0]}")


if __name__ == '__main__':
    main()
