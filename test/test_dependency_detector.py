from brain.developer.dependency_detector import DependencyDetector

files = {

    "main.py": """

import flask

import requests

import cv2

from ultralytics import YOLO

"""

}

detector = DependencyDetector()

result = detector.detect(files)

print(result.python)

print(result.javascript)