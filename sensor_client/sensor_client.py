import time
import schedule
import prometheus_client

# import DHT_lib
import board
from adafruit_bme280 import basic as adafruit_bme280

# Temperature, Pressure, Humidity, Pressure@Sea_Level, Height
metrics_names = ['temperature', 'humidity', 'pressure', 'altitude']
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

def set_gauges():
    for metric, measure in zip(metrics, get_extended_measurements()):
        metric.set(measure)
        print(f"{metric}: {measure}")
    print()


def get_extended_measurements():
    try:
        i2c = board.I2C()  # uses board.SCL and board.SDA
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        bme280.sea_level_pressure = 1015.
        return [bme280.temperature, bme280.humidity, bme280.pressure, bme280.altitude]
    except ValueError:
        print("WARNING: Failed to measuring Adafruit.")
        return [-999., -1., -1., -999]


# def get_measurements():
#     # simple_measurements = get_simple_measurements()
#     extended_measurements = get_extended_measurements()
#     return [0, 0., 0.] + extended_measurements


if __name__ == '__main__':
    prometheus_client.start_http_server(8000)
    schedule.every(15).seconds.do(set_gauges)
    while True:
        schedule.run_pending()
        time.sleep(1)
