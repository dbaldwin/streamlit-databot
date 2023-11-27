import pickle

from databot.PyDatabot import PyDatabot, DatabotConfig, start_databot_webserver, PyDatabotSaveToQueueDataCollector

from utils.sensor_constants import DATABOT_DATA_FILE

def main():
    with open("streamlit_databot_config.pkl", "rb") as f:
        c = pickle.load(f)

    c.address = PyDatabot.get_databot_address()

    db = PyDatabotSaveToQueueDataCollector(c)

    t =start_databot_webserver(queue_data_collector=db, host="localhost", port=8321)

    db.run()


if __name__ == '__main__':
    main()