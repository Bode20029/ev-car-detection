import time
import threading
from queue import Queue
import logging
import os
from playsound import playsound
from dotenv import load_dotenv

load_dotenv()

# Import sensor functionalities
from hc_sr04p_distance import get_distance, GPIO_setup, GPIO_cleanup
from Updated_PZEM_Sensor_Reader_Script import connect_to_sensor, read_sensor_data
from line_notify import LineNotifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for system logic
DISTANCE_THRESHOLD = 20  # cm
CURRENT_THRESHOLD = 0.05  # A

# LINE Notify token
LINE_NOTIFY_TOKEN = "J0oQ74OftbCNdiPCCfV4gs75aqtz4aAL8NiGfHERvZ4"

class SensorManager:
    def __init__(self):
        self.data_queue = Queue()
        
        # Set up GPIO for HC-SR04P
        GPIO_setup()
        
        # Set up PZEM
        self.pzem_master = connect_to_sensor()

        # Set up LINE Notifier
        self.line_notifier = LineNotifier(LINE_NOTIFY_TOKEN)

        # Alert state
        self.alert_active = False

    def pzem_thread(self):
        while True:
            try:
                pzem_data = read_sensor_data(self.pzem_master)
                self.data_queue.put(('pzem', pzem_data['current_A']))
            except Exception as e:
                logger.error(f"Error reading PZEM data: {e}")
                self.pzem_master = connect_to_sensor()  # Reconnect
            time.sleep(5)

    def distance_thread(self):
        while True:
            distance = get_distance()
            if distance is not None:
                self.data_queue.put(('distance', distance))
            time.sleep(5)

    def process_data(self):
        while True:
            sensor1, data1 = self.data_queue.get()
            sensor2, data2 = self.data_queue.get()
            
            if sensor1 == 'pzem' and sensor2 == 'distance':
                current, distance = data1, data2
            elif sensor1 == 'distance' and sensor2 == 'pzem':
                distance, current = data1, data2
            else:
                continue

            print(f"{current:.2f} {distance:.2f}")

            if current > CURRENT_THRESHOLD and distance < DISTANCE_THRESHOLD:
                if not self.alert_active:
                    self.alert_active = True
                    message = "Alert: Current > 0.05A and Distance < 20cm"
                    logger.info(message)
                    self.line_notifier.send_notification(message)
                    threading.Thread(target=self.play_alert).start()
            else:
                self.alert_active = False

    def play_alert(self):
        while self.alert_active:
            playsound('alert.mp3')

    def run(self):
        threads = [
            threading.Thread(target=self.pzem_thread),
            threading.Thread(target=self.distance_thread),
            threading.Thread(target=self.process_data)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def cleanup(self):
        GPIO_cleanup()
        if self.pzem_master:
            self.pzem_master.close()

if __name__ == "__main__":
    manager = SensorManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info("Program stopped by user")
    finally:
        manager.cleanup()
        logger.info("Cleanup completed")