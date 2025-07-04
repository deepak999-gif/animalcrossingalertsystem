import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import torch
import time
from PIL import Image


# ----------- Load YOLOv5 model -----------
def load_model():
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    return model


# ----------- Play alarm sound safely -----------
import pygame
import numpy as np


def play_alarm():
    sample_rate = 44100
    duration = 4  # seconds
    frequency = 1000  # Hz
    amplitude = 1

    t = np.linspace(0, duration, int(sample_rate * duration), False)
    beep = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Convert to 16-bit PCM (pygame requires 16-bit or 32-bit integer data)
    beep_int16 = np.int16(beep * 32767)  # Convert to 16-bit signed PCM

    # Create stereo sound by duplicating the signal (for stereo channels)
    beep_stereo = np.column_stack((beep_int16, beep_int16))  # Create stereo (2 channels)

    # Make sure the array is C-contiguous
    beep_stereo_contiguous = np.ascontiguousarray(beep_stereo)

    # Initialize pygame mixer
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=2)  # 16-bit, stereo

    # Play the sound
    sound = pygame.sndarray.make_sound(beep_stereo_contiguous)  # Create a sound object
    sound.play()

    pygame.time.wait(int(duration * 1000))  # Wait for the sound to finish


# ----------- Real-time detection function -----------
def detect_from_webcam(model):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Webcam not accessible")
        return

    harmful_animals = { "deer", "rabbit", "boar", 'dog', "monkey", "elephant", "cow", "goat", "horse"}
    last_alert_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to PIL Image for YOLO
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = model(img)
        df = results.pandas().xyxy[0]

        detected_animals = set()

        for _, row in df.iterrows():
            label = row['name']
            if label in harmful_animals:
                detected_animals.add(label)

        # Alert logic
        # Alert logic

        if detected_animals and (time.time() - last_alert_time > 5):
            print(f"⚠️ Alert! Harmful animals detected: {label}")
            threading.Thread(target=play_alarm).start()
            last_alert_time = time.time()

        # Show live webcam feed
        cv2.imshow("Animal Detector - Press 'q' to exit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_and_display():
    # Start the animal detection process
    print("Starting webcam detection...")
    model = load_model()
    detect_from_webcam(model)


# ----------- GUI Setup -----------
root = tk.Tk()
root.title("Animal Detection System")

# Add a button that will start the detection process
button = tk.Button(root, text="Start Detection", command=lambda: threading.Thread(target=detect_and_display).start())
button.pack()

root.mainloop()

