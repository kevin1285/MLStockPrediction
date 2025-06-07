#!/usr/bin/env python3
"""
Convert Keras model to TensorFlow Lite format for memory optimization
Run this once to create the .tflite model file
"""

import tensorflow as tf
import os

# Paths
KERAS_MODEL_PATH = 'ml_models/MulticlassPAP_20k_v2.keras'
TFLITE_MODEL_PATH = 'ml_models/MulticlassPAP_20k_v2.tflite'

def convert_keras_to_tflite():
    print("Loading Keras model...")
    try:
        # Load the Keras model
        model = tf.keras.models.load_model(KERAS_MODEL_PATH, compile=False)
        print(f"Model loaded successfully. Input shape: {model.input_shape}")
        
        # Convert to TensorFlow Lite
        print("Converting to TensorFlow Lite...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Optional: Enable optimizations to reduce model size further
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Convert the model
        tflite_model = converter.convert()
        
        # Save the model
        with open(TFLITE_MODEL_PATH, 'wb') as f:
            f.write(tflite_model)
        
        print(f"TensorFlow Lite model saved to: {TFLITE_MODEL_PATH}")
        
        # Show size comparison
        keras_size = os.path.getsize(KERAS_MODEL_PATH) / (1024 * 1024)  # MB
        tflite_size = os.path.getsize(TFLITE_MODEL_PATH) / (1024 * 1024)  # MB
        
        print(f"Original Keras model size: {keras_size:.2f} MB")
        print(f"TensorFlow Lite model size: {tflite_size:.2f} MB")
        print(f"Size reduction: {((keras_size - tflite_size) / keras_size * 100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    if not os.path.exists(KERAS_MODEL_PATH):
        print(f"Error: Keras model not found at {KERAS_MODEL_PATH}")
        exit(1)
    
    success = convert_keras_to_tflite()
    if success:
        print("✅ Conversion completed successfully!")
        print("You can now update your requirements.txt and pap.py to use TensorFlow Lite")
    else:
        print("❌ Conversion failed!")
        exit(1) 