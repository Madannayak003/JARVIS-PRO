from brain.developer.engine.project_integrity_validator import (
    ProjectIntegrityValidator
)

expected = [

    "display/lcd.cpp",
    "display/lcd.h",

    "rfid/rfid.cpp",
    "rfid/rfid.h",

    "servo/servo.cpp",
    "servo/servo.h",

    "wifi/wifi_manager.cpp",
    "wifi/wifi_manager.h",

    "firebase/firebase_manager.cpp",
    "firebase/firebase_manager.h",

]

generated = {

    "display/lcd.cpp": "code",
    "display/lcd.h": "code",

    "rfid/rfid.cpp": "code",
    # rfid.h missing

    "servo/servo.cpp": "code",
    "servo/servo.h": "code",

    "wifi/wifi_manager.cpp": "code",
    "wifi/wifi_manager.h": "code",

    "firebase/firebase_manager.cpp": "",
    "firebase/firebase_manager.h": "code",

    "extra.cpp": "code"

}

validator = ProjectIntegrityValidator()

result = validator.validate(

    expected,

    generated

)

print("=" * 60)
print("SUCCESS :", result.success)

print("\nMISSING")
for f in result.missing:
    print("-", f)

print("\nUNEXPECTED")
for f in result.unexpected:
    print("-", f)

print("\nEMPTY")
for f in result.empty_files:
    print("-", f)

print("\nDUPLICATES")
for f in result.duplicates:
    print("-", f)