from brain.developer.project.technology_detector import TechnologyDetector

detector = TechnologyDetector()

profile = detector.detect(

    "Create ESP32 RFID Door Lock using MFRC522 Servo LCD WiFi Firebase"

)

print("=" * 60)
print(profile)