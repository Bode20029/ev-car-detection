import serial
import struct
import time

# Initialize the serial connection to the PZEM-004T
# Replace '/dev/ttyUSB0' with the appropriate port on your Jetson Nano
serial_port = '/dev/ttyUSB0'
baud_rate = 9600

def read_pzem(serial_connection):
    # Request packet to send to PZEM-004T
    request_packet = b'\xB0\xC0\xA8\x01\x01\x00\x01\x5A'

    # Send the request packet to the PZEM-004T
    serial_connection.write(request_packet)
    
    # Read the response from the PZEM-004T
    response = serial_connection.read(7)

    # Check if the response length is as expected
    if len(response) == 7:
        # Unpack the data from the response
        data = struct.unpack('>HBBH', response[1:])
        
        voltage = data[0] / 10.0  # Voltage in Volts
        current = (data[1] << 8 | data[2]) / 100.0  # Current in Amperes
        power = data[3] / 10.0  # Power in Watts
        
        return {
            'voltage': voltage,
            'current': current,
            'power': power
        }
    else:
        return None

def main():
    try:
        # Open the serial connection
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            while True:
                # Read data from the PZEM-004T
                data = read_pzem(ser)
                
                if data:
                    print(f"Voltage: {data['voltage']} V")
                    print(f"Current: {data['current']} A")
                    print(f"Power: {data['power']} W")
                else:
                    print("Failed to read data")
                
                # Wait for a while before the next read
                time.sleep(1)
                
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Program terminated by user")

if __name__ == '__main__':
    main()