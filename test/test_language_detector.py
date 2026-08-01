from brain.developer.language_detector import LanguageDetector

detector = LanguageDetector()

tests = [

    "python",

    "HTML",

    "React",

    "ESP32",

    "fix login page",

    "tell me a joke",

    "calculator"

]

for t in tests:

    print(f"{t:20} -> {detector.is_language(t)}")