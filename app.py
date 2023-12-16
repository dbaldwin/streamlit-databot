import json
import logging
import pickle
import platform
import subprocess
import threading
import time
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.WARNING)


import altair as alt
import pandas as pd
import requests
import streamlit as st
from databot.PyDatabot import DatabotConfig

from utils.sensor_constants import DATABOT_DATA_FILE
from utils.sidebar_utils import setup_input_selection_sidebar, get_display_fields_from_sensor_table, \
    get_save_fields_from_sensor_table

st.set_page_config(
    page_title="DroneBlocks Databot Dashboard",
    page_icon="🧠",
    layout="wide",
)

def get_sensor_values_to_display():
    sensor_select_df = st.session_state.updated_sensor_df
    display_chart_df = sensor_select_df.query("display == True").sort_values(by="friendly_name")
    json_records = json.loads(display_chart_df.to_json(orient='records'))

    return json_records


def get_run_mode(): # return stop/start/pause
    return st.session_state.get('run_mode', default='stop')


# ****************************************************
#           CLICK HANDLERS
# ****************************************************

def continue_btn_on_click():
    st.session_state.run_mode = 'start'


def pause_btn_on_click():
    st.session_state.run_mode = 'pause'


def stop_collecting_data_on_click():
    """
    Stop collecting data on click.

    This method is responsible for stopping the collection of data. It terminates the pydatabot_process, if it exists in the st.session_state, and deletes it from the session state. It also
    * sets the read_data_flag, data_refresh, and run_mode in the session state to their respective default values.

    Parameters:
        None

    Returns:
        None

    Example usage:
        stop_collecting_data_on_click()
    """
    if 'pydatabot_process' in st.session_state:
        try:
            st.session_state.pydatabot_process.terminate()
            time.sleep(0.2)
        except Exception as e:
            st.error("Could not terminate data collection process")
            logging.exception("Could not terminate data collector", exc_info=e)
        finally:
            del st.session_state['pydatabot_process']

    st.session_state['read_data_flag'] = False
    st.session_state['data_refresh'] = False
    st.session_state.run_mode = 'stop'


def _get_data_from_webserver_save_to_file(datafile_path: str, refresh_rate: int):
    """

    This method `_get_data_from_webserver_save_to_file` is responsible for continuously fetching data from a web server and saving it to a file.

    Parameters:
    - `datafile_path` (str): The path to the file where the data will be saved.
    - `refresh_rate` (int): The refresh rate in milliseconds, indicating how often to fetch new data from the web server.

    Returns:
    - This method does not have a return value.

    Here is an example usage:

    ```python
    datafile_path = "/path/to/datafile.txt"
    refresh_rate = 5000

    _get_data_from_webserver_save_to_file(datafile_path, refresh_rate)
    ```

    The method starts a web server thread that runs indefinitely. Within the thread, it repeatedly performs the following steps:
    1. Sleeps for the specified `refresh_rate` in milliseconds.
    2. Makes a GET request to the web server at `http://localhost:8321`.
    3. Retrieves the response as JSON data.
    4. Appends the JSON data to the file specified by `data_path_file`, followed by a newline character.

    If a `requests.ConnectionError` occurs, it means that the web server has gone away, so the thread can exit gracefully.

    If any other exception occurs during the execution of the method, it will be logged and the thread will sleep for 1 second before continuing.

    Once the web server thread is exited, a debug log indicating the exit will be generated.

    """
    logging.debug(f"start web server thread: {datafile_path}, {refresh_rate}")
    while True:
        try:
            time.sleep(refresh_rate / 1000)
            data_record = requests.get(url="http://localhost:8321").json()
            with datafile_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data_record))
                f.write("\n")

        except requests.ConnectionError as conn_error:
            # webserver must have gone away so we can exit this thread
            break

        except Exception as exc:
            logging.debug(exc)
            time.sleep(1)

    logging.debug("**** EXIT webserver thread")


def collect_data_on_click():
    """
    Collects data when the user clicks a button.

    This method collects data only if certain conditions are met. It checks if the 'pydatabot_process' key is not present in the session state of the Streamlit app. If the 'run_mode_flag
    *' key is present in the session state and its value is 'Launch Databot script', it proceeds to collect the data.

    First, it sets the 'datafile_path' key in the session state to the value of DATABOT_DATA_FILE.

    Next, it checks if the data file exists and removes it if it does.

    Then, it creates a DatabotConfig object using the create_databot_config() function.

    After that, it saves the DatabotConfig object to a file named 'streamlit_databot_config.pkl'.

    Depending on the operating system, it sets the 'shell_flag' variable to either True or False.

    Next, it starts a subprocess that runs the 'pydatabot_run_webserver.py' script using the 'python' command. The subprocess is started in the current directory and with the shell flag
    * depending on the operating system.

    A separate thread is started to continuously get data from the web server and save it to the data file. The thread runs the _get_data_from_webserver_save_to_file() function with the
    * arguments DATABOT_DATA_FILE and the value of 'databot_data_refresh_rate' from the session state. The thread is started as a daemon thread to ensure it exits when the main thread exits
    *.

    Finally, it sets the 'read_data_flag' key in the session state to True and sets the 'run_mode' key to 'start'.

    """
    if 'pydatabot_process' not in st.session_state:
        if 'run_mode_flag' in st.session_state and st.session_state['run_mode_flag'] == 'Launch Databot script':
            st.session_state['datafile_path'] = DATABOT_DATA_FILE
            # remove datafile
            if Path(DATABOT_DATA_FILE).exists():
                Path(DATABOT_DATA_FILE).unlink()
            databot_config: DatabotConfig = create_databot_config()
            with open("streamlit_databot_config.pkl", "wb") as f:
                pickle.dump(databot_config, f)
            # windows needs shell=True, macos shell=False
            shell_flag = st.session_state.is_windows
            st.session_state.pydatabot_process = subprocess.Popen(["python", "pydatabot_save_data_to_file.py"],
                                                                  cwd=Path(".").absolute(), shell=shell_flag)
            # st.session_state.pydatabot_process = subprocess.Popen(["python", "pydatabot_run_webserver.py"],
            #                                                       cwd=Path(".").absolute(), shell=shell_flag)

            t = threading.Thread(target=_get_data_from_webserver_save_to_file,
                                 args=(DATABOT_DATA_FILE, st.session_state['databot_data_refresh_rate']), daemon=True)
            t.start()

            st.session_state.webserver_thread = t
    st.session_state['read_data_flag'] = True
    st.session_state.run_mode = 'start'


def read_databot_data_file(status_placeholder) -> pd.DataFrame | None:
    try:
        datafile_path = st.session_state.get('datafile_path', default=DATABOT_DATA_FILE)
        if get_run_mode() == 'start':
            # look for the file to watch
            datafile_path = st.session_state['datafile_path']
            if datafile_path:
                while not Path(datafile_path).exists():
                    status_placeholder.warning(f"Waiting for file: {datafile_path}")
                    time.sleep(1)

        if not datafile_path:
            return None

        status_placeholder.success(f"Reading from datafile: {datafile_path}")

        df = pd.read_json(path_or_buf=datafile_path, lines=True)
        # only pull out the columns for the selected sensors.
        columns_to_drop = st.session_state.updated_sensor_df.query("display == False")['data_columns'].to_list()
        columns_to_drop = [item for sublist in columns_to_drop for item in sublist]
        df = df.drop(columns=columns_to_drop, errors='ignore')
        if get_run_mode() == 'start':
            if df.shape[1] == 2:
                # means all we have are the time and the timestamp columns which means the
                # script to save values is not saving the values selected in the checkbox list
                st.error(f"The script to save databot values does not save the sensors selected.  Make sure you have selected all of the sensors in the save data script that you might want to see in the Dashboard")

        df.sort_values(by=['time'], ascending=False, inplace=True)
        if st.session_state['number_of_samples_to_display'] > 0:
            df = df.head(st.session_state['number_of_samples_to_display'])
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
        logging.debug(field)
        data_columns = field['data_columns']
        if len(data_columns) == 1:
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
    if get_run_mode() == 'start':
        with placeholder_component.container():
            # st.info("Reading datafile...")
            df = read_databot_data_file(status_placeholder)
            if df is not None:
                st.session_state.last_df = df
                _display_dataframe_data(df)
    else:
        # get the last dataframe read to display that
        with placeholder_component.container():
            # st.info("Reading datafile...")
            df = read_databot_data_file(status_placeholder)
            if df is not None:
                _display_dataframe_data(df)


def main():
    st.header("DroneBlocks databot2.0™ Dashboard")
    setup_input_selection_sidebar()
    # tab1, tab2 = st.tabs(["Dashboard", "Sensor Map"])
    tab1 = st.tabs(["Dashboard"])
    if 'read_data_flag' not in st.session_state:
        st.session_state['read_data_flag'] = False

    with tab1[0]:
        status_placeholder = st.empty()
        col1, col2, col3 = st.columns(3)
        st.divider()
        with col1:  # start button
            if st.session_state.get('run_mode', default='stop') == 'stop':
                st.button("Start Reading Data", key='collect_data_btn', on_click=collect_data_on_click, disabled=False)
            elif get_run_mode() == 'start' or get_run_mode() == 'pause':
                st.button("Start Reading Data", key='collect_data_btn', disabled=True)

        with col2:  # stop button
            if get_run_mode() == 'stop':
                st.button("Stop Reading Data", key="stop_collect_data_btn", disabled=True)
            elif get_run_mode() == 'start' or get_run_mode() == 'pause':
                st.button("Stop Reading Data", key="stop_collect_data_btn", on_click=stop_collecting_data_on_click,
                          disabled=False)

        with col3:  # pause/continue button
            if get_run_mode() == 'stop':
                st.button("Pause Reading Data", key="pause_collect_data_btn", disabled=True)
            elif get_run_mode() == 'start':
                st.button("Pause Reading Data", key="pause_collect_data_btn", disabled=False,
                          on_click=pause_btn_on_click)
            elif get_run_mode() == 'pause':
                st.button("Continue Reading Data", key="pause_collect_data_btn", disabled=False,
                          on_click=continue_btn_on_click)

        placeholder = st.empty()

        # ************************************************
        #           DATABOT DISPLAY EVENT LOOP
        # ************************************************
        try:
            while get_run_mode() == 'start':
                draw_dashboard(placeholder, status_placeholder)
                time.sleep(1)
        except Exception as exc:
            pass

        try:
            if get_run_mode() == 'stop' or get_run_mode() == 'pause':
                draw_dashboard(placeholder, status_placeholder)
        except:
            pass
        finally:
            time.sleep(0.2)


@st.cache_data
def init_app_once():
    st.session_state['data_refresh'] = False
    st.session_state.run_mode = 'stop'  # 'start', 'stop', 'pause'
    st.session_state.last_df = None
    if 'datafile_path' not in st.session_state:
        st.session_state['datafile_path'] = DATABOT_DATA_FILE

    if "windows" in platform.system().lower():
        st.session_state.is_windows = True
    else:
        st.session_state.is_windows = False

    return 1


if __name__ == '__main__':
    init_app_once()
    main()