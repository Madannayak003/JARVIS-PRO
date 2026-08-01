from core.fallback import fallback

SKILLS = {}

def register(action, handler):

    # print("[REGISTER]", action)

    SKILLS[action] = handler


def execute(action, data):
    
    print("Requested action :", repr(action))
    print("Available actions:", sorted(SKILLS.keys()))

    handler = SKILLS.get(action)

    if handler:

        return handler(data)

    print(f"\nUnknown action : {action}")

    print("\nTrying AI fallback...\n")

    print(fallback(action))

    return False


def list_skills():
    return list(SKILLS.keys())