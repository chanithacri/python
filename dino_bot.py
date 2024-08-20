import time
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten

# Setup Chrome browser with Selenium using webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument("--mute-audio")
options.add_argument("--disable-gpu")
# Remove headless option
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1024, 768)

# Open the dino game URL (ensure you have a network disconnection to access the dino game)
driver.get("chrome://dino")

# Function to send jump command
def jump():
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)

# Function to capture the game screen
def capture_screen():
    driver.save_screenshot("dino_screen.png")
    image = Image.open("dino_screen.png")
    return np.array(image)

# Function to process image and detect obstacles
def detect_obstacle(screen):
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    roi = gray[300:360, 150:250]
    _, thresh = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY_INV)
    obstacle_frame = cv2.resize(thresh, (100, 60))
    obstacle_frame = np.expand_dims(obstacle_frame, axis=-1)  # Adding channel dimension
    return obstacle_frame / 255.0  # Normalizing the frame

# Create a neural network model
def create_model(input_shape):
    model = Sequential([
        Flatten(input_shape=input_shape),
        Dense(128, activation='relu'),
        Dense(128, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Create and train the model
input_shape = (60, 100, 1)  # Adjusted to include channel dimension
model = create_model(input_shape)

# Load pre-trained weights, if available
try:
    model.load_weights("dino_weights.h5")
except Exception as e:
    print(f"Could not load weights: {str(e)}")

# Start the game using JavaScript
driver.execute_script("document.getElementsByClassName('runner-canvas')[0].runner_.play();")
time.sleep(2)

try:
    while True:
        screen = capture_screen()
        processed_screen = detect_obstacle(screen)
        
        # Make a prediction using the AI model
        prediction = model.predict(np.expand_dims(processed_screen, axis=0))

        if prediction > 0.5:
            jump()
        time.sleep(0.05)
except KeyboardInterrupt:
    driver.quit()
