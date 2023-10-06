import dataclasses
import pickle
import platform
import subprocess
import time
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from databot.PyDatabot import DefaultDatabotConfig, DatabotConfig
from streamlit_image_coordinates import streamlit_image_coordinates

from hotspots.databot_image_map import find_image_map_entry
from utils.databot_image_utils import find_box, read_image, read_hot_spots
from utils.sensor_constants import DATABOT_DATA_FILE, DATABOT_HOTSPOTS_DATA, DATABOT_IMAGE_PATH
from utils.sidebar_utils import setup_input_selection_sidebar, get_display_fields_from_sensor_table, \
    get_save_fields_from_sensor_table

st.set_page_config(
    page_title="DroneBlocks Databot Dashboard",
    page_icon="✅",
    layout="wide",
)


# ****************************************************
#           CLICK HANDLERS
# ****************************************************

def continue_btn_on_click():
    st.session_state.run_mode = 'start'


def pause_btn_on_click():
    print("****** PAUSE")
    st.session_state.run_mode = 'pause'


def stop_collecting_data_on_click():
    if 'pydatabot_process' in st.session_state:
        st.session_state.pydatabot_process.terminate()
        del st.session_state['pydatabot_process']

    st.session_state['read_data_flag'] = False
    st.session_state['data_refresh'] = False
    st.session_state.run_mode = 'stop'


def collect_data_on_click():
    if 'pydatabot_process' not in st.session_state:
        if 'run_mode_flag' in st.session_state and st.session_state['run_mode_flag'] == 'Launch Databot script':
            # remove datafile
            if Path(DATABOT_DATA_FILE).exists():
                Path(DATABOT_DATA_FILE).unlink()
            databot_config: DatabotConfig = create_databot_config()
            with open("streamlit_databot_config.pkl", "wb") as f:
                pickle.dump(databot_config, f)
            # windows needs shell=True, macos shell=False
            if "windows" in platform.system().lower():
                shell_flag = True
            else:
                shell_flag = False
            st.session_state.pydatabot_process = subprocess.Popen(["python", "pydatabot_save_data_to_file.py"],
                                                                  cwd=Path(".").absolute(), shell=shell_flag)
    st.session_state['read_data_flag'] = True
    st.session_state.run_mode = 'start'


def read_databot_data_file(status_placeholder) -> pd.DataFrame | None:
    try:
        datafile_path = DATABOT_DATA_FILE
        if 'run_mode_flag' in st.session_state and st.session_state['run_mode_flag'] == 'Read from a Databot file':
            # look for the file to watch
            datafile_path = st.session_state['datafile_path']
            if datafile_path:
                while not Path(datafile_path).exists():
                    status_placeholder.warning(f"Waiting for file: {datafile_path}")
                    time.sleep(1)

        status_placeholder.success(f"Reading from datafile: {datafile_path}")

        df = pd.read_json(path_or_buf=datafile_path, lines=True)
        df.sort_values(by=['time'], ascending=False, inplace=True)
        return df
    except Exception as exc:
        return None


def create_databot_config() -> DatabotConfig:
    databot_config = DatabotConfig()
    checked_save_records = get_save_fields_from_sensor_table()
    for checked_save_record in checked_save_records:
        setattr(databot_config, checked_save_record['sensor_name'], True)
    databot_config.refresh = st.session_state['databot_data_refresh_rate']

    return databot_config


def _display_dataframe_data(df: pd.DataFrame):
    if df is None:
        return

    st.write(f":cyan[Number of records read: {df.shape[0]}]")

    # if the pydata is processing/collecting data
    # then check to see if we should stop collecting
    if 'pydatabot_process' in st.session_state:
        number_of_samples_to_collect = st.session_state['number_of_samples_to_collect']
        if number_of_samples_to_collect > 0 and df.shape[0] >= number_of_samples_to_collect:
            stop_collecting_data_on_click()
            return

    st.dataframe(df, use_container_width=True)
    display_fields_records = get_display_fields_from_sensor_table()
    for field in display_fields_records:
        data_columns = field['data_columns']
        if len(data_columns) == 1:
            # then there is only a single metric for this sensor
            number_of_samples_to_display = st.session_state.get('number_of_samples_to_display', default=0)
            if number_of_samples_to_display > 0:
                df = df.head(number_of_samples_to_display)
            # st.line_chart(df, x="time", y=data_column, use_container_width=True)
            try:
                st.divider()
                st.write(field['friendly_name'])
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
                number_of_samples_to_display = st.session_state.get('number_of_samples_to_display', 0)
                if number_of_samples_to_display > 0:
                    df_sensor_values = df_sensor_values.head(number_of_samples_to_display)

                st.divider()
                st.write(field['friendly_name'])
                c = alt.Chart(df_sensor_values).transform_fold(field['data_columns'],
                                                               as_=['sensor_name', 'sensor_value']
                                                               ).mark_line().encode(x='time:T',
                                                                                    y='sensor_value:Q',
                                                                                    color='sensor_name:N')
                st.altair_chart(c, use_container_width=True)
            except:
                pass


def draw_dashboard(placeholder_component, status_placeholder):
    if st.session_state.run_mode == 'start':
        with placeholder_component.container():
            st.info("Reading datafile...")
            df = read_databot_data_file(status_placeholder)
            if df is not None:
                st.session_state.last_df = df
                _display_dataframe_data(df)
    else:
        # get the last dataframe read to display that
        with placeholder_component.container():
            st.info("Reading datafile...")
            df = read_databot_data_file(status_placeholder)
            if df is not None:
                _display_dataframe_data(df)


def highlight_selected_sensor(db_image):
    fields = dataclasses.fields(DefaultDatabotConfig)
    for field in fields:
        checkbox_key = f"{field.name}_save_cb"
        if checkbox_key in list(st.session_state.keys()):
            if st.session_state[checkbox_key] == True:
                key, value = find_image_map_entry(checkbox_key.split("_")[0])


def main():
    st.header("DroneBlocks databot2.0 Dashboard")
    setup_input_selection_sidebar()
    tab1, tab2 = st.tabs(["Dashboard", "Sensor Map"])
    if 'read_data_flag' not in st.session_state:
        st.session_state['read_data_flag'] = False

    with tab1:
        status_placeholder = st.empty()
        col1, col2, col3 = st.columns(3)
        st.divider()
        with col1:  # start button
            if st.session_state.run_mode == 'stop':
                st.button("Start Reading Data", key='collect_data_btn', on_click=collect_data_on_click, disabled=False)
            elif st.session_state.run_mode == 'start' or st.session_state.run_mode == 'pause':
                st.button("Start Reading Data", key='collect_data_btn', disabled=True)

        with col2:  # stop button
            if st.session_state.run_mode == 'stop':
                st.button("Stop Reading Data", key="stop_collect_data_btn", disabled=True)
            elif st.session_state.run_mode == 'start' or st.session_state.run_mode == 'pause':
                st.button("Stop Reading Data", key="stop_collect_data_btn", on_click=stop_collecting_data_on_click,
                          disabled=False)

        with col3:  # pause/continue button
            if st.session_state.run_mode == 'stop':
                st.button("Pause Reading Data", key="pause_collect_data_btn", disabled=True)
            elif st.session_state.run_mode == 'start':
                st.button("Pause Reading Data", key="pause_collect_data_btn", disabled=False,
                          on_click=pause_btn_on_click)
            elif st.session_state.run_mode == 'pause':
                st.button("Continue Reading Data", key="pause_collect_data_btn", disabled=False,
                          on_click=continue_btn_on_click)

        placeholder = st.empty()

        # ************************************************
        #           DATABOT DISPLAY EVENT LOOP
        # ************************************************
        try:
            while st.session_state.run_mode == 'start':
                draw_dashboard(placeholder, status_placeholder)
                time.sleep(1)
        except Exception as exc:
            pass

        try:
            if st.session_state.run_mode == 'stop' or st.session_state.run_mode == 'pause':
                draw_dashboard(placeholder, status_placeholder)
        except:
            pass
        finally:
            time.sleep(0.2)

    with tab2:
        st.write("Sensor Map")
        hotspots_df = read_hot_spots(DATABOT_HOTSPOTS_DATA)
        st.dataframe(hotspots_df)
        st.write(hotspots_df.shape)
        the_image = read_image(DATABOT_IMAGE_PATH)
        # st.image(image=the_image)

        # highlight_selected_sensor(the_image)

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


@st.cache_data
def init_app_once():
    print("**** init app")
    st.session_state['data_refresh'] = False
    st.session_state.run_mode = 'stop'  # 'start', 'stop', 'pause'
    st.session_state.last_df = None
    return 1


if __name__ == '__main__':
    init_app_once()
    main()
