import board
import digitalio
import busio
import time
import adafruit_bme280
import sqlite3 as sql
import datetime as date

from flask import Flask

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# OR create library object using our Bus SPI port
#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
#bme_cs = digitalio.DigitalInOut(board.D10)
#bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, bme_cs)

# change this to match the location's pressure (hPa) at sea level
bme280.sea_level_pressure = 1013.25

app = Flask(__name__)


@app.route('/')
def index():
    
    db = sql.connect('sensorData.db')

    temp = bme280.temperature
    humidity = bme280.humidity
    pressure = bme280.pressure

    if float(temp) > 40.0 or float(temp) < -5.0:
        temp = getAverageTemperature(db)

    saveInDatabase(db, temp, humidity, pressure)
    sensorData = formatSensorData(temp, humidity, pressure)
    print(sensorData)

    db.close()
    return sensorData

def getAverageTemperature(db):
    cursor = db.cursor()
    cursor.execute("SELECT AVG(temperature) FROM (SELECT timestamp, temperature FROM readings ORDER BY timestamp DESC LIMIT 20)")
    return cursor.fetchone()

def formatSensorData(temp, humidity, pressure):
    json = "{"
    json += '"temperature": ' + "{0:.1f}".format(temp) + ", "
    json += '"humidity": ' + "{0:.1f}".format(humidity) + ", "
    json += '"pressure": ' + "{0:.1f}".format(pressure)
    json += "}"
    return json

def saveInDatabase(db, temp, humidity, pressure):
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS readings(timestamp DATETIME PRIMARY KEY, temperature DECIMAL, humidity DECIMAL, pressure DECIMAL)")
    cursor.execute('''INSERT INTO readings VALUES(?, ?, ?, ?)''', (date.datetime.now(), temp, humidity, pressure))
    db.commit()


if __name__ == '__main__':
   app.run(debug=False, host='0.0.0.0')

"""
while True:
    print(getSensorData())
    saveInDb()
    time.sleep(2)
"""
