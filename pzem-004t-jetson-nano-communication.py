import serial
import time

# Configure the serial port
ser = serial.Serial(
    port='/dev/ttyTHS1',  # This may vary depending on your Jetson Nano setup
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

def read_pzem_004t():
    # PZEM-004T command to read all electrical parameters
    command = bytes([0xF8, 0x04, 0x00, 0x00, 0x00, 0x0A, 0x64, 0x64])
    
    # Send command
    ser.write(command)
    
    # Read response
    response = ser.read(25)
    
    if len(response) == 25 and response[0] == 0xF8 and response[1] == 0x04:
        voltage = int.from_bytes(response[3:5], byteorder='big') / 10.0  # V
        current = int.from_bytes(response[5:7], byteorder='big') / 1000.0  # A
        power = int.from_bytes(response[7:11], byteorder='big') / 10.0  # W
        energy = int.from_bytes(response[11:15], byteorder='big')  # Wh
        frequency = int.from_bytes(response[15:17], byteorder='big') / 10.0  # Hz
        pf = int.from_bytes(response[17:19], byteorder='big') / 100.0
        
        return {
            'voltage': voltage,
            'current': current,
            'power': power,
            'energy': energy,
            'frequency': frequency,
            'power_factor': pf
        }
    else:
        return None

try:
    while True:
        data = read_pzem_004t()
        if data:
            print(f"Voltage: {data['voltage']} V")
            print(f"Current: {data['current']} A")
            print(f"Power: {data['power']} W")
            print(f"Energy: {data['energy']} Wh")
            print(f"Frequency: {data['frequency']} Hz")
            print(f"Power Factor: {data['power_factor']}")
            print("-------------------------")
        else:
            print("Failed to read data")
        
        time.sleep(5)  # Wait for 5 seconds before next reading

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    ser.close()
    print("Serial port closed")
