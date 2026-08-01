from brain.developer.analyzer.detectors.board_detector import BoardDetector


def main():

    detector = BoardDetector()

    tests = [

        "Build Arduino Uno robot",

        "Create Arduino Mega project",

        "ESP32 weather station",

        "ESP8266 IoT",

        "NodeMCU MQTT",

        "Raspberry Pi AI Camera",

        "Python calculator",

    ]

    for text in tests:

        context = detector.create_context(text)
        result = detector.detect(context)

        print(f"{text:<40} -> {result}")


if __name__ == "__main__":
    main()