# test_process.py

import psutil

for p in psutil.process_iter(["pid", "name"]):
    try:
        if "whatsapp" in p.info["name"].lower():
            print(p.info)
    except:
        pass