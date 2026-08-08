from core.registry import register

from voice.manager import speak

from services.whatsapp_api import (open_whatsapp,close_whatsapp)

from services.whatsapp_api import (send_message,send_photo,send_file)

from services.file_manager import (latest_photo,latest_screenshot,find_file)

from services.contact_manager import (resolve_contact)

from core.file_selection_memory import (set_files,clear_files)

from core.file_selection_memory import (get_files,clear_files)

from core.whatsapp_memory import (
    set_contact,
    get_contact,
    clear_contact,
    set_pending_message,
    get_pending_message,
    clear_pending_message
)

def whatsapp_open(data):

    if open_whatsapp():

        speak("Opening WhatsApp.")

    else:

        speak("Unable to open WhatsApp.")

    return True


def whatsapp_close(data):

    close_whatsapp()

    speak("Closing WhatsApp.")

    return True

def whatsapp_send_message(data):

    contact = resolve_contact(
    data.get("contact", "").strip()
    )
    message = data.get("message", "").strip()

    if not contact:

        set_pending_message(message)

        speak("Which contact should I send it to?")

        return True

    if not message:

        speak("What should I send?")

        return True

    speak(f"Sending your message to {contact}.")

    ok = send_message(contact, message)

    if ok:

        speak("Message sent.")

    else:

        speak("I couldn't send the message.")

    return True

def whatsapp_send_latest_photo(data):

    contact = resolve_contact(
        data.get("contact", "").strip()
    )

    photo = latest_photo()

    if not photo:

        speak("I couldn't find any recent photo.")

        return True

    speak(f"Sending the latest photo to {contact}.")

    ok = send_photo(
        contact,
        str(photo)
    )

    if ok:

        speak("Photo sent.")

    else:

        speak("I couldn't send the photo.")

    return True

def whatsapp_send_latest_screenshot(data):

    contact = resolve_contact(
        data.get("contact", "").strip()
    )

    image = latest_screenshot()

    if not image:

        speak("I couldn't find any screenshot.")

        return True

    speak(f"Sending the latest screenshot to {contact}.")

    ok = send_photo(
        contact,
        str(image)
    )

    if ok:

        speak("Screenshot sent.")

    else:

        speak("I couldn't send the screenshot.")

    return True

def whatsapp_send_file(data):

    contact = resolve_contact(
        data.get("contact", "").strip()
    )

    filename = data.get("filename", "").strip()

    matches = find_file(filename)

    if not matches:

        speak(f"I couldn't find {filename}.")

        return True

    # Only one file
    if len(matches) == 1:

        file = matches[0]

        speak(f"Sending {file.name} to {contact}.")

        ok = send_file(
            contact,
            str(file)
        )

        if ok:

            speak("File sent.")

        else:

            speak("I couldn't send the file.")

        return True

    # Multiple files

    set_files({

        "contact": contact,

        "files": matches

    })

    speak(f"I found {len(matches)} matching files.")

    for i, file in enumerate(matches[:5], 1):

        speak(f"{i}. {file.name}")

    speak("Which one should I send?")

    return True

def whatsapp_send_selected_file(data):

    pending = get_files()

    if not pending:

        speak("There isn't any pending file selection.")

        return True

    files = pending["files"]
    contact = pending["contact"]

    index = data["index"]

    if index >= len(files):

        speak("That option doesn't exist.")

        return True

    file = files[index]

    speak(f"Sending {file.name}.")

    ok = send_file(
        contact,
        str(file)
    )

    clear_files()

    if ok:

        speak("File sent.")

    else:

        speak("Unable to send the file.")

    return True

def whatsapp_wait_contact(data):

    set_pending_message("")

    speak("Which contact should I send it to?")

    return True

def whatsapp_wait_message(data):

    contact = data["contact"]

    set_contact(contact)

    print("[WA] Stored contact:", get_contact())

    speak(f"What would you like me to send to {contact}?")

    return True

register("whatsapp_open", whatsapp_open)
register("whatsapp_close", whatsapp_close)
register("whatsapp_send_message", whatsapp_send_message)
register("whatsapp_wait_message", whatsapp_wait_message)

register(
    "whatsapp_send_latest_photo",
    whatsapp_send_latest_photo
)

register(
    "whatsapp_send_latest_screenshot",
    whatsapp_send_latest_screenshot
)

register(
    "whatsapp_send_file",
    whatsapp_send_file
)

register(
    "whatsapp_send_selected_file",
    whatsapp_send_selected_file
)

register(
    "whatsapp_wait_contact",
    whatsapp_wait_contact
)