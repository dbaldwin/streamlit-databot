from databot.PyDatabot import PyDatabot, DatabotConfig, PyDatabotSaveToFileDataCollector


def main():
    c = DatabotConfig()
    c.accl = True
    c.Laccl = True
    c.gyro = True
    c.magneto = True
    c.address = PyDatabot.get_databot_address()
    db = PyDatabotSaveToFileDataCollector(c, file_name="./test_data.txt", number_of_records_to_collect=20)
    db.run()


if __name__ == '__main__':
    main()
