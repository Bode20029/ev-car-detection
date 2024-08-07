import cv2
import time
from object_detection import process_frame
from bluetooth_connection import find_bluetooth_speaker, connect_to_speaker
from text_to_speech import text_to_speech
from audio_playback import play_audio

def check_stationary(frames, threshold=0.95):
    # Simple check to see if the last few frames are similar
    if len(frames) < 2:
        return False
    
    similarity = cv2.compareHist(
        cv2.calcHist([frames[-1]], [0], None, [256], [0, 256]),
        cv2.calcHist([frames[-2]], [0], None, [256], [0, 256]),
        cv2.HISTCMP_CORREL
    )
    return similarity > threshold

def main():
    # Connect to Bluetooth speaker
    speaker_address = find_bluetooth_speaker()
    if not speaker_address:
        print("Bluetooth speaker not found")
        return
    
    bluetooth_sock = connect_to_speaker(speaker_address)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    frame_buffer = []
    stationary_start_time = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_buffer.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        if len(frame_buffer) > 10:  # Keep last 10 frames
            frame_buffer.pop(0)
        
        if check_stationary(frame_buffer):
            if stationary_start_time is None:
                stationary_start_time = time.time()
            elif time.time() - stationary_start_time > 5:  # 5 seconds have passed
                if process_frame(frame):
                    message = "This is a space reserved for EV charging only"
                    text_to_speech(message)
                    play_audio('output.mp3')
                    time.sleep(5)  # Wait before detecting again
                    stationary_start_time = None  # Reset timer
        else:
            stationary_start_time = None  # Reset timer if movement detected
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    bluetooth_sock.close()

if __name__ == "__main__":
    main()