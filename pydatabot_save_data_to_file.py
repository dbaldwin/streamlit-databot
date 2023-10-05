import pickle

from databot.PyDatabot import PyDatabot, PyDatabotSaveToFileDataCollector
from utils.sensor_constants import DATABOT_DATA_FILE

def main():
    with open("streamlit_databot_config.pkl", "rb") as f:
        c = pickle.load(f)

    c.address = PyDatabot.get_databot_address()
    db = PyDatabotSaveToFileDataCollector(c, file_name=DATABOT_DATA_FILE)
    db.run()


if __name__ == '__main__':
    main()
