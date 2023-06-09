import datetime
import json
import time

import requests
import schedule
import prometheus_client

# import DHT_lib
import board
from adafruit_bme280 import basic as adafruit_bme280


class Status:
    change_trigger = None
    status = None

    def call(self):
        when = datetime.datetime.now() - datetime.timedelta(hours=2)
        key = when.strftime('%Y-%m-%dT%H:00')
        if not self.change_trigger == key:
            url = 'https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json'
            response = requests.get(url)
            if response.status_code//100 != 2:
                raise ConnectionError()
            data = json.loads(response.text)

            target_sensor = '7240919'
            target_data = 'pressao'

            self.change_trigger = key
            self.status = data.get(key).get(target_sensor).get(target_data)
        return self.status


# Temperature, Pressure, Humidity, Pressure@Sea_Level, Height
metrics_names = ['temperature', 'humidity', 'pressure', 'altitude', 'sea_level_pressure']
metrics: list[prometheus_client.Gauge] = [
    prometheus_client.Gauge(
        name=name,
        documentation=name,
    ) for name in metrics_names
]


# dht = DHT_lib.DHT(11)
#
#
# def get_simple_measurements():
#     chk = dht.read_DHT11()
#     # if chk is 0:
#     #     print('ok')
#     # print("chk : %d, \t Humidity : %.2f, \t Temperature : %.2f " % (chk, dht.humidity, dht.temperature))
#
#     return [chk, dht.humidity, dht.temperature]


def set_gauges(pressure_status):
    for metric, measure in zip(metrics, get_extended_measurements(pressure_status)):
        metric.set(measure)
        print(f"{metric}: {measure}")
    print()


def get_extended_measurements(pressure_status):
    try:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        bme280.sea_level_pressure = pressure_status.call()
        return [bme280.temperature, bme280.humidity, bme280.pressure, bme280.altitude, bme280.sea_level_pressure]
    except ValueError:
        print("WARNING: Failed to measuring Adafruit.")
        return [-999., -1., -1., -999, -999]


# def get_measurements():
#     # simple_measurements = get_simple_measurements()
#     extended_measurements = get_extended_measurements()
#     return [0, 0., 0.] + extended_measurements


if __name__ == '__main__':
    pressure = Status()
    prometheus_client.start_http_server(8000)
    schedule.every(15).seconds.do(set_gauges, pressure)
    while True:
        schedule.run_pending()
        time.sleep(1)
