import os
import json
import numpy as np
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from tensorflow import lite as tflite

load_dotenv()

# MQTT configurations
detection_topic = 'serial-reader/data'
mqtt_broker = 'localhost'
mqtt_port = 1883

# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set('iot-application', 'iot-application')

# Load the TF Lite model
model_path = 'env_model.tflite'
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(detection_topic)
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        temperature = data.get('temperature')
        pressure = data.get('pressure')
        humidity = data.get('humidity')

        if temperature is not None and pressure is not None and humidity is not None:
            input_data = np.array([[temperature, pressure, humidity]], dtype=np.float32)
            print("Received data:", temperature, pressure, humidity)

            # Get input and output details of the model
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            # Set the input tensor
            interpreter.set_tensor(input_details[0]['index'], input_data)

            # Perform inference
            interpreter.invoke()

            # Get the prediction
            prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
            print("Prediction:", prediction)

            # Determine the environment status
            if prediction >= 0.5:
                detection_data = {"detected": "true"}
            else:
                detection_data = {"detected": "false"}

            print(detection_data)

    except Exception as e:
        print(f"Error processing message: {e}")

# Assign MQTT client callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    # Connect to MQTT broker and start loop
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()

except KeyboardInterrupt:
    print("Disconnecting from MQTT broker")
    mqtt_client.disconnect()

except Exception as e:
    print(f"Error: {e}")
    mqtt_client.disconnect()