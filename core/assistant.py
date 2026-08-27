import time

from voice.manager import speak, stop_speaking
from config.settings import WAKE_WORDS

from core.confirmation import waiting
from core.confirmation import get
from core.confirmation import clear

from core.registry import execute

from core.listener import start_listener
from core.listener import get_command

from core.runtime import handle_priority

from core.dispatcher import dispatch

from core.action_memory import set_memory

from core.interrupt import interrupt

from skills.assistant.greetings import startup_greeting

from core.whatsapp_memory import (
    get_contact,
    clear_contact,
    get_pending_message,
    clear_pending_message,
)

from core.context import (
    add_message,
    get_value,
    set_value,
)

from core.power import (
    sleep,
    wake,
    shutdown,
)

from core.busy_manager import (
    is_busy,
    ask_switch,
)

from ai.intent import detect
from core.fast_router import fast_route


# ============================================================
# NATURAL CONVERSATION / BRAIN
# ============================================================

from brain.natural.natural_bridge import (
    natural_conversation_bridge,
)

from brain import (
    conversation,
    profile,
    state as brain_state,
    conversation_context,
)

from hud.integration import HUDIntegration


# ============================================================
# RUN
# ============================================================

def run():

    speak(startup_greeting())

    start_listener()

    while True:

        # =====================================================
        # HUD — Waiting for user input
        # =====================================================

        HUDIntegration.listening()

        query = get_command()

        if not query:

            time.sleep(0.05)

            continue

        # =====================================================
        # HUD — JARVIS is processing the command
        # =====================================================

        HUDIntegration.thinking()

        # =====================================================
        # New user input preempts TTS
        # =====================================================

        stop_speaking()

        # =====================================================
        # HIGH PRIORITY RUNTIME EVENTS
        # =====================================================

        if handle_priority(query):

            time.sleep(0.05)

            continue

        query = query.strip()

        # =====================================================
        # WAITING FOR WHATSAPP MESSAGE
        # =====================================================

        pending = get_pending_message()

        if pending is not None:

            clear_pending_message()

            dispatch(
                f"message {query}"
            )

            continue

        # =====================================================
        # WAITING FOR WHATSAPP CONTACT
        # =====================================================

        contact = get_contact()

        print(
            "[WA] Pending contact:",
            contact
        )

        if contact:

            clear_contact()

            dispatch(
                f"message {contact} {query}"
            )

            continue

        # =====================================================
        # EXISTING CONFIRMATION
        # =====================================================

        if waiting():

            q = query.lower()

            pending = get()

            # -------------------------------------------------
            # Busy Manager Confirmation
            # -------------------------------------------------

            if (
                pending
                and
                pending.get("action") == "switch_task"
            ):

                if q in [
                    "yes",
                    "sure",
                    "okay",
                    "ok",
                    "go ahead",
                    "continue",
                    "yes please",
                    "yes continue",
                    "yes do it",
                    "yes switch",
                ]:

                    new_command = (
                        pending["new_command"]
                    )

                    interrupt()

                    clear()

                    dispatch(
                        new_command
                    )

                    continue

                elif q in [
                    "no",
                    "no thanks",
                    "never mind",
                    "stay",
                    "keep going",
                ]:

                    speak(
                        "Okay. I'll ignore the new request."
                    )

                    clear()

                    continue

            # -------------------------------------------------
            # Search Platform Clarification
            # -------------------------------------------------

            if (
                pending
                and
                "context" in pending
            ):

                ctx = pending["context"]

                if "pending_search" in ctx:

                    platforms = {
                        "google": "google_search",
                        "youtube": "youtube_search",
                        "github": "github_search",
                        "chatgpt": "chatgpt_search",
                    }

                    for platform, action in platforms.items():

                        if platform in q:

                            set_memory(
                                "search_platform",
                                platform,
                            )

                            execute(
                                action,
                                {
                                    "query":
                                        ctx[
                                            "pending_search"
                                        ]
                                },
                            )

                            clear()

                            break

                    if not waiting():

                        continue

                    pending = get()

            # -------------------------------------------------
            # Normal Confirmation
            # -------------------------------------------------

            if q in [
                "yes",
                "yes sir",
                "confirm",
                "do it",
                "okay",
                "ok",
            ]:

                pending = get()

                execute(
                    pending["action"],
                    pending["data"],
                )

                clear()

                continue

            elif q in [
                "no",
                "cancel",
                "stop",
                "don't",
                "dont",
            ]:

                speak("Cancelled.")

                set_value(
                    "chat_mode",
                    False,
                )

                clear()

                continue

        # =====================================================
        # NATURAL CONVERSATION
        #
        # ConversationRequest is now the common NCI interface.
        #
        # NCI only understands the request here.
        # It does NOT execute anything.
        # =====================================================

        conversation_request = None

        try:

            conversation_request = (
                natural_conversation_bridge.process(

                    user_input=query,

                    conversation_context=(
                        conversation_context
                    ),

                    conversation_manager=(
                        conversation
                    ),

                    profile_manager=(
                        profile
                    ),

                    state_manager=(
                        brain_state
                    ),

                    ai_context=None,
                )
            )

            print(
                "[NCI REQUEST]",
                conversation_request,
            )

        except Exception as e:

            print(
                "[NCI REQUEST] "
                f"Analysis failed safely: {e}"
            )

            conversation_request = None

        # =====================================================
        # NCI FOLLOW-UP PREEMPTION
        #
        # ConversationRequest is authoritative for the
        # semantic understanding of the current request.
        #
        # Dispatcher remains responsible for execution.
        # =====================================================

        nci_follow_up = (

            conversation_request is not None

            and

            conversation_request.relation
            in {
                "follow_up",
                "continuation",
                "correction",
                "reference",
            }
        )

        if nci_follow_up:

            print(
                "[NCI PREEMPT] "
                "Contextual follow-up detected."
            )

            print(
                "[NCI PREEMPT RELATION]",
                conversation_request.relation,
            )

            print(
                "[NCI PREEMPT REQUEST]",
                conversation_request,
            )

            print(
                "[NCI PREEMPT] "
                "Sending command to dispatcher."
            )

            interrupt()

            dispatch(
                query,
                conversation_request=conversation_request,
            )

            continue

        # =====================================================
        # ACTIVE TASK / CONVERSATION PREEMPTION
        # =====================================================

        if is_busy():

            # =================================================
            # FAST ACTION PREEMPTION
            # =================================================

            fast_plan = fast_route(
                query
            )

            if fast_plan:

                print(
                    "[FAST PREEMPT] "
                    "Immediate deterministic command detected."
                )

                print(
                    "[FAST PREEMPT PLAN]",
                    fast_plan,
                )

                interrupt()

                dispatch(
                    query,
                    fast_plan=fast_plan,
                )

                continue

            # =================================================
            # CHAT PREEMPTION
            # =================================================

            mode = detect(
                query
            )

            if mode == "chat":

                print(
                    "[CHAT PREEMPT] "
                    "New conversational request detected."
                )

                interrupt()

                dispatch(
                    query,
                    fast_plan=fast_plan,
                )

                continue

            # =================================================
            # LONG-RUNNING TASK
            # =================================================

            ask_switch(
                query
            )

            speak(
                f"I'm still working on your previous request.\n"
                f'Should I stop it and continue with "{query}"?'
            )

            continue

        # =====================================================
        # POWER STATE
        # =====================================================

        power_state = get_value(
            "state"
        )

        if power_state == "sleep":

            if query.startswith(
                "jarvis"
            ):

                wake()

            continue

        # =====================================================
        # SLEEP
        # =====================================================

        if query.lower() in [

            "go offline",
            "sleep",
            "go sleep mode",

        ]:

            sleep()

            continue

        # =====================================================
        # SHUTDOWN
        # =====================================================

        if query.lower() in [

            "shutdown",
            "terminate",
            "go terminate"
            "power off",

        ]:

            shutdown()

            continue

        # =====================================================
        # EXISTING CONTEXT MESSAGE
        # =====================================================

        add_message(
            "user",
            query
        )

        # =====================================================
        # WAKE WORDS
        # =====================================================

        if any(
            query.startswith(word)
            for word in WAKE_WORDS
        ):

            remaining = query

            for word in WAKE_WORDS:

                if remaining.startswith(word):

                    remaining = (
                        remaining
                        .replace(
                            word,
                            "",
                            1,
                        )
                        .strip()
                    )

                    break

            if remaining == "":

                if power_state == "sleep":

                    wake()

                else:

                    speak(
                        "Yes Sir."
                    )

                continue

            speak(
                "Yes Sir."
            )

            dispatch(
                remaining
            )

            continue

        # =====================================================
        # NORMAL DISPATCH
        # =====================================================

        dispatch(
            query,
            conversation_request=conversation_request,
        )