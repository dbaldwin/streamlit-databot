import time

from databot.PyDatabot import PyDatabot, PyDatabotSaveToFileDataCollector, DatabotConfig

from utils.sensor_constants import DATABOT_DATA_FILE


def main():
    c = DatabotConfig()
    c.accl = True
    c.alti = True
    c.ambLight = True
    c.pressure = True
    c.co2 = True
    c.Etemp1 = True
    c.Etemp2 = True
    c.gyro = True
    c.hum = True
    c.Laccl = True
    c.magneto = True
    c.UV = True
    c.voc = True
    c.Sdist = True
    c.address = PyDatabot.get_databot_address()

    c.address = PyDatabot.get_databot_address()
    print(f"Save data to file: {DATABOT_DATA_FILE}")
    time.sleep(2)
    db = PyDatabotSaveToFileDataCollector(c, file_name=DATABOT_DATA_FILE)
    db.run()


if __name__ == '__main__':
    main()
