import json
from typing import List

import pandas as pd
import streamlit as st

from .sensor_constants import databot_sensors


def get_display_fields_from_sensor_table() -> List[dict]:
    sensor_select_df = st.session_state.updated_sensor_df
    display_chart_df = sensor_select_df.query("display == True").sort_values(by="friendly_name")
    json_records = json.loads(display_chart_df.to_json(orient='records'))

    return json_records

def get_save_fields_from_sensor_table() -> List[dict]:
    return get_display_fields_from_sensor_table()
    # # it is possible that someone will just click display,
    # # so to do what seems reasonable, look for save or display
    # sensor_select_df = st.session_state.updated_sensor_df
    # display_chart_df = sensor_select_df.query("save == True | display == True").sort_values(by="friendly_name")
    # json_records = json.loads(display_chart_df.to_json(orient='records'))
    #
    # return json_records


@st.cache_data
def get_databot_sensor_table():
    df = pd.DataFrame(data=databot_sensors.values()).sort_values(by="friendly_name")
    return df


def display_databot_sensors_from_df(tab_container, include_save_to_file: bool = True):
    df = get_databot_sensor_table()
    column_config = {
        "friendly_name": st.column_config.TextColumn(
            label="Sensor Name"
        ),
        "save": st.column_config.CheckboxColumn(
                                    label="Save To File"
                                ),
        "display": st.column_config.CheckboxColumn(
            label="Save & Display"
        )
    }
    column_order = ("friendly_name", "save", "display",)
    if not include_save_to_file:
        column_order = ("friendly_name", "display",)


    with tab_container:
        st.header("Databot Sensors")
        updated_sensor_df = st.data_editor(df,
                       column_config=column_config,
                       key="sensor_table",
                       disabled=("friendly_name",),
                       hide_index=True,
                       column_order=column_order,
                       use_container_width=True,
                       height=600
        )
        st.session_state.updated_sensor_df = updated_sensor_df


def setup_input_selection_sidebar():
    with st.sidebar:
        st.title("Data Collection Config")
        st.divider()
        if st.session_state.is_windows:
            run_mode = st.radio(label='How would you like to read databot2.0™ data',
                                options=['Read from a Databot file'],
                                captions=['Read data from an existing file, which can be updated by a separate PyDatabot application.'],
                                help='Reading from a file will not launch a process, but instead just read from a file that may be static, or being populated by a different script reading from the databot.',
                                key="run_mode_flag")
        else:
            run_mode = st.radio(label='How would you like to read databot2.0™ data',
                                options=['Launch Databot script', 'Read from a Databot file'],
                                captions=['Run a script that will collect data in real time. \nThis will launch a databot process to read sensor values and save them to a file.', 'Read data from an existing file, which can be updated by a separate PyDatabot application.'],
                                help='Launching a script will run a python script in a separate process that will write data to a file and display that data.  Reading from a file will not launch a process, but instead just read from a file that may be static, or being populated by a different script reading from the databot.',
                                key="run_mode_flag")

        st.divider()

        if run_mode == 'Launch Databot script' and not st.session_state.is_windows:
            tab1, tab2 = st.tabs(['Databot Sensors', 'Collection Config'])
            display_databot_sensors_from_df(tab1, include_save_to_file=False)

            with tab2:
                st.header("Databot Refresh Rate in milliseconds")
                cols = st.columns(2)
                with cols[0]:
                    pass

                with cols[1]:
                    st.number_input(label="Refresh rate in ms", min_value=100, max_value=1000000, value=1000, step=100,
                                    key="databot_data_refresh_rate")
                st.divider()

                st.header("Display the last 'n' number of data samples.")
                col4, col5 = st.columns(2)
                with col4:
                    st.write("Set to zero for all data values")

                with col5:
                    st.number_input(label="Number of samples to display", min_value=0, max_value=300, value=0, step=1,
                                    key="number_of_samples_to_display")

                st.divider()
                st.header("Total number of samples to collect")
                col6, col7 = st.columns(2)
                with col6:
                    st.write("Set to zero for unlimited datapoints")
                with col7:
                    st.number_input(label="Number of samples to collect", min_value=0, max_value=5000, value=0, step=1,
                                    key="number_of_samples_to_collect")

        else:
            tab1, tab2 = st.tabs(['Databot Sensors', 'Data File Config'])
            display_databot_sensors_from_df(tab1, include_save_to_file=False)

            with tab2:
                st.header("Data file configuration")
                st.text("Use this configuration if you want to read a Databot json")
                st.text("data file that is being created by another process")
                st.divider()
                read_datafile_path = st.session_state.get('datafile_path', default="")
                last_datafile_path = st.text_input(label='JSON Data File', value=read_datafile_path, placeholder="Full path to the Databot JSON data file",
                              key="read_datafile_path")
                st.session_state['datafile_path'] = last_datafile_path

                st.divider()

                st.header("Display the last 'n' number of data samples.")
                col4, col5 = st.columns(2)
                with col4:
                    st.write("Set to zero for all data values")

                with col5:
                    st.number_input(label="Number of samples to display", min_value=0, max_value=300, value=0, step=1,
                                    key="number_of_samples_to_display")
