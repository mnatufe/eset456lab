import serial
import pynmea2
import paho.mqtt.client as mqtt
import time
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 4800
BROKER_IP = '127.0.0.1'
TOPIC = 'pi/gps'
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "gps_publisher")
client.connect(BROKER_IP, 1883)
client.loop_start()
with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
  while True:
    try:
      line = ser.readline().decode('ascii', errors='replace').strip()
      if line.startswith('$GPRMC') or line.startswith('$GNRMC'):
        msg = pynmea2.parse(line)
        if msg.status == 'A': # A = active fix, V = void (no fix)
          payload = (f"lat={msg.latitude:.6f},"
            f"lng={msg.longitude:.6f},"
            f"time={msg.timestamp}")
        else:
           payload = "status=no_fix"
        client.publish(TOPIC, payload)
        print(f"Published: {payload}")
    except pynmea2.ParseError:
      pass
    time.sleep(1)
