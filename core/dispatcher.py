from click import command

from ai.intent import detect

from core.task_manager import task_manager
from core.workers import chat_worker
from core.planner_worker import planner_worker

from core.action_memory import (
    get_memory,
    set_memory,
)

from core.executor import execute_ai_plan

from ai.memory_pipeline import learn
from ai.memory_view import show_all
from ai.memory_intent import handle as memory_forget
from ai.memory_profile import profile_summary

from core.context import (
    get_value,
    set_value,
)

from ai.memory_stats import (
    total,
    by_category,
)

from brain.brain_router import BrainRouter

brain_router = BrainRouter()

from core.fast_router import fast_route

from core.registry import execute

from brain.screen_followup import is_screen_followup

from brain.conversation_coordinator import conversation_coordinator

# =========================================================
# DISPATCHER
# =========================================================

def dispatch(
    command,
    skip_fast=False,
    fast_plan=None,
):

    command = command.strip()

    if not command:
        return

    # =====================================================
    # CLARIFICATION CONTEXT
    # =====================================================

    clarify = get_memory(
        "clarify_context"
    )

    if clarify:

        subject = clarify.get(
            "subject"
        )

        ctype = clarify.get(
            "type"
        )

        if ctype == "generic_action":

            cmd = command.lower()

            # -------------------------------------------------
            # Google
            # -------------------------------------------------

            if cmd in [
                "google",
                "search google",
                "search on google",
                "on google",
            ]:

                set_memory(
                    "clarify_context",
                    None,
                )

                execute_ai_plan(
                    [
                        {
                            "action": "google_search",
                            "query": subject,
                        }
                    ],
                    task_manager.event(
                        "planner"
                    ),
                )

                return

            # -------------------------------------------------
            # YouTube
            # -------------------------------------------------

            elif cmd in [
                "youtube",
                "search youtube",
                "search on youtube",
                "on youtube",
            ]:

                set_memory(
                    "clarify_context",
                    None,
                )

                execute_ai_plan(
                    [
                        {
                            "action": "youtube_search",
                            "query": subject,
                        }
                    ],
                    task_manager.event(
                        "planner"
                    ),
                )

                return

            # -------------------------------------------------
            # GitHub
            # -------------------------------------------------

            elif cmd in [
                "github",
                "search github",
            ]:

                set_memory(
                    "clarify_context",
                    None,
                )

                execute_ai_plan(
                    [
                        {
                            "action": "github_search",
                            "query": subject,
                        }
                    ],
                    task_manager.event(
                        "planner"
                    ),
                )

                return

            # -------------------------------------------------
            # ChatGPT
            # -------------------------------------------------

            elif cmd in [
                "chatgpt",
                "search chatgpt",
            ]:

                set_memory(
                    "clarify_context",
                    None,
                )

                execute_ai_plan(
                    [
                        {
                            "action": "chatgpt_search",
                            "query": subject,
                        }
                    ],
                    task_manager.event(
                        "planner"
                    ),
                )

                return

    # =====================================================
    # FAST ROUTE
    # =====================================================
    #
    # There are now TWO possible ways to reach here:
    #
    # 1. Normal dispatch:
    #
    #       dispatch(command)
    #
    #       → dispatcher calculates fast_plan
    #
    # 2. FAST PREEMPTION:
    #
    #       assistant.py calculates fast_plan
    #
    #       → interrupt()
    #
    #       → dispatch(
    #             command,
    #             fast_plan=fast_plan
    #         )
    #
    # In case #2 we reuse the existing plan.
    #
    # This prevents:
    #
    #       fast_route()
    #       fast_route()
    #
    # for the same command.
    # =====================================================

    if not skip_fast:

        # -------------------------------------------------
        # Reuse existing plan if assistant already
        # calculated it.
        # -------------------------------------------------

        if fast_plan is None:

            fast_plan = fast_route(
                command
            )

        # -------------------------------------------------
        # Execute FAST plan
        # -------------------------------------------------

        if fast_plan:

            print(
                "[DISPATCHER] "
                "Fast route handled command:",
                fast_plan,
            )

            for action in fast_plan:

                action_name = action.get(
                    "action"
                )

                if not action_name:
                    continue

                result = execute(
                    action_name,
                    action,
                )

                print(
                    "[DISPATCHER RESULT]",
                    repr(result),
                )

                # =========================================
                # NATURAL CONVERSATION
                # Record successful execution AFTER the
                # existing skill has executed.
                #
                # IMPORTANT:
                # This ONLY records context.
                # It does NOT execute anything.
                # =========================================

                try:

                    conversation_coordinator.record_execution(

                        topic=action.get(
                            "topic"
                        ),

                        task=action.get(
                            "task"
                        ),

                        application=action.get(
                            "app"
                            or action.get("application")
                        ),

                        skill=action.get(
                            "skill"
                        ),

                        intent=action.get(
                            "intent"
                        ),

                        action=action_name,

                        object=action.get(
                            "object"
                        ),

                        objects=action.get(
                            "objects"
                        ),

                        result=result,

                    )

                    print(
                        "[CONVERSATION EXECUTION]",
                        conversation_coordinator.context.snapshot(),
                    )

                except Exception as e:

                    # -------------------------------------
                    # CRITICAL SAFETY RULE
                    #
                    # Natural Conversation must NEVER
                    # break the existing dispatcher.
                    # -------------------------------------

                    print(
                        "[CONVERSATION] "
                        f"Execution context update failed: {e}"
                    )

                # -----------------------------------------
                # Speak skill result
                # -----------------------------------------

                if result is not None:

                    from voice.manager import speak

                    # -------------------------------------
                    # Boolean result
                    # -------------------------------------

                    if isinstance(
                        result,
                        bool,
                    ):

                        if action_name == "vision_check":

                            message = (
                                "Yes, I can see it."
                                if result
                                else "No, I don't see it."
                            )

                            speak(
                                message
                            )

                    # -------------------------------------
                    # Dictionary result
                    # -------------------------------------

                    elif isinstance(
                        result,
                        dict,
                    ):

                        if "error" in result:

                            speak(
                                result["error"]
                            )

                        else:

                            speak(
                                str(result)
                            )

                    # -------------------------------------
                    # Normal result
                    # -------------------------------------

                    else:

                        speak(
                            str(result)
                        )

            return

    # =====================================================
    # SCREEN CONTEXT FOLLOW-UP
    # =====================================================

    if is_screen_followup(
        command
    ):

        from voice.manager import speak

        print(
            "[SCREEN FOLLOWUP] "
            "Routing request through conversational context."
        )

        task_manager.start(
            "chat",
            chat_worker,
            command,
        )

        return

    # =====================================================
    # DEVELOPER INTENT
    # =====================================================

    mode = detect(
        command
    )

    if mode == "developer":

        from voice.manager import speak

        print(
            "[DEVELOPER] Request detected."
        )

        speak(
            "Developer request received."
        )

        # -------------------------------------------------
        # Send directly to Brain Router
        # -------------------------------------------------

        brain_result = brain_router.route(
            command
        )

        if brain_result.handled:

            print(
                "[BRAIN ROUTER] "
                f"{brain_result.module} "
                "module handled request."
            )

            # ---------------------------------------------
            # Developer Result
            # ---------------------------------------------

            if (
                brain_result.module
                == "developer"
            ):

                result = (
                    brain_result.result
                )

                if result is None:

                    speak(
                        "Developer request completed."
                    )

                    return

                if result.success:

                    # -------------------------------------
                    # Developer CREATE result
                    # -------------------------------------

                    if hasattr(
                        result,
                        "files",
                    ):

                        files = []

                        for file in result.files:

                            path = getattr(
                                file,
                                "path",
                                "",
                            )

                            if (
                                path
                                and path not in files
                            ):

                                files.append(
                                    path
                                )

                        if files:

                            message = (
                                "Developer project "
                                "created successfully. "
                                f"Created {len(files)} files."
                            )

                        else:

                            message = (
                                "Developer project "
                                "created successfully."
                            )

                    # -------------------------------------
                    # Developer EDIT result
                    # -------------------------------------

                    elif hasattr(
                        result,
                        "patches",
                    ):

                        files = []

                        for patch in result.patches:

                            path = getattr(
                                patch,
                                "path",
                                "",
                            )

                            if (
                                path
                                and path not in files
                            ):

                                files.append(
                                    path
                                )

                        if files:

                            if len(files) == 1:

                                message = (
                                    "Developer edit "
                                    "completed. "
                                    f"Modified {files[0]}."
                                )

                            else:

                                message = (
                                    "Developer edit "
                                    "completed. "
                                    f"Modified {len(files)} files."
                                )

                        else:

                            message = (
                                "Developer edit "
                                "completed successfully."
                            )

                    # -------------------------------------
                    # Unknown Developer result
                    # -------------------------------------

                    else:

                        message = (
                            "Developer request "
                            "completed successfully."
                        )

                    print(
                        "[DEVELOPER RESULT]"
                    )

                    print(
                        message
                    )

                    speak(
                        message
                    )

                else:

                    errors = getattr(
                        result,
                        "errors",
                        [],
                    )

                    print(
                        "[DEVELOPER ERROR]"
                    )

                    for error in errors:

                        print(
                            error
                        )

                    speak(
                        "The Developer request failed."
                    )

                return

        # ---------------------------------------------
        # Developer request detected but not handled
        # ---------------------------------------------

        print(
            "[DEVELOPER] "
            "Request was not handled."
        )

        speak(
            "I received the Developer request, "
            "but I could not execute it."
        )

        return

    # =====================================================
    # ACTION MEMORY
    # =====================================================

    memory_result = learn(
        command
    )

    # =====================================================
    # MEMORY SAVED
    # =====================================================

    if memory_result.get(
        "saved"
    ):

        print(
            f"[MEMORY] Saved -> "
            f"{memory_result['key']} = "
            f"{memory_result['value']}"
        )

        from voice.manager import speak

        if memory_result.get(
            "updated"
        ):

            speak(
                f"I've updated your "
                f"{memory_result['key']}."
            )

        else:

            speak(
                "I'll remember that."
            )

        return

    # =====================================================
    # ALREADY KNOWN
    # =====================================================

    if memory_result.get(
        "already_known"
    ):

        from voice.manager import speak

        print(
            "[MEMORY] Already known."
        )

        speak(
            "I already knew that."
        )

        return

    # =====================================================
    # SHOW STORED MEMORIES
    # =====================================================

    MEMORY_VIEW_COMMANDS = (

        "show my memories",
        "list my memories",
        "show all memories",
        "what do you know about me",
        "show everything you know",

    )

    if command in MEMORY_VIEW_COMMANDS:

        from voice.manager import speak

        result = show_all()

        print(
            "\n[MEMORY VIEW]\n"
        )

        print(
            result
        )

        speak(
            result
        )

        return

    # =====================================================
    # USER PROFILE
    # =====================================================

    PROFILE_COMMANDS = (

        "show my profile",
        "my profile",
        "user profile",
        "profile",
        "summarize me",
        "summarize my profile",

    )

    if command in PROFILE_COMMANDS:

        from voice.manager import speak

        profile = profile_summary()

        print(
            "\n[USER PROFILE]\n"
        )

        print(
            profile
        )

        speak(
            profile
        )

        return

    # =====================================================
    # MEMORY STATISTICS
    # =====================================================

    MEMORY_STATS_COMMANDS = (

        "memory statistics",
        "memory stats",
        "show memory statistics",
        "how many memories do you have",
        "how many things do you remember",

    )

    if command in MEMORY_STATS_COMMANDS:

        from voice.manager import speak

        count = total()

        categories = by_category()

        text = (
            f"I currently remember "
            f"{count} thing"
        )

        if count != 1:

            text += "s"

        text += ".\n"

        for category, value in categories.items():

            text += (
                f"\n{category.title()} : {value}"
            )

        print(
            "\n[MEMORY STATS]\n"
        )

        print(
            text
        )

        speak(
            text
        )

        return

    # =====================================================
    # FORGET MEMORY
    # =====================================================

    forget_result = memory_forget(
        command
    )

    if forget_result:

        from voice.manager import speak

        print(
            "\n[MEMORY FORGET]\n"
        )

        print(
            forget_result
        )

        if (
            forget_result["type"]
            == "key"
        ):

            message = (
                f"I forgot your "
                f"{forget_result['key']}."
            )

        elif (
            forget_result["type"]
            == "category"
        ):

            deleted = len(
                forget_result["deleted"]
            )

            message = (
                f"I forgot "
                f"{deleted} "
                f"memories from "
                f"{forget_result['category']}."
            )

        else:

            deleted = len(
                forget_result["deleted"]
            )

            message = (
                f"I forgot "
                f"{deleted} memories."
            )

        speak(
            message
        )

        return

    # =====================================================
    # PENDING SEARCH SUBJECT
    # =====================================================

    pending = get_memory(
        "pending_subject"
    )

    if (
        pending
        and command.startswith("search on")
    ):

        platform = (
            command
            .replace(
                "search on",
                "",
                1,
            )
            .strip()
        )

        print(
            "[PENDING SUBJECT]",
            pending,
        )

        if platform == "youtube":

            execute_ai_plan(
                [
                    {
                        "action": "youtube_search",
                        "query": pending,
                    }
                ],
                task_manager.event(
                    "planner"
                ),
            )

            set_memory(
                "pending_subject",
                None,
            )

            return

        elif platform == "google":

            execute_ai_plan(
                [
                    {
                        "action": "google_search",
                        "query": pending,
                    }
                ],
                task_manager.event(
                    "planner"
                ),
            )

            set_memory(
                "pending_subject",
                None,
            )

            return

        elif platform == "github":

            execute_ai_plan(
                [
                    {
                        "action": "github_search",
                        "query": pending,
                    }
                ],
                task_manager.event(
                    "planner"
                ),
            )

            set_memory(
                "pending_subject",
                None,
            )

            return

    # =====================================================
    # GENERIC SEARCH USING ACTION MEMORY
    # =====================================================

    if (
        command.startswith("search ")
        and "youtube" not in command
        and "google" not in command
        and "github" not in command
        and "chatgpt" not in command
    ):

        current_site = get_memory(
            "site"
        )

        query = (
            command
            .replace(
                "search",
                "",
                1,
            )
            .strip()
        )

        # -------------------------------------------------
        # YouTube
        # -------------------------------------------------

        if current_site == "youtube":

            print(
                "[ACTION MEMORY] "
                "YouTube Search"
            )

            task_manager.start(
                "executor",
                execute_ai_plan,
                [
                    {
                        "action": "youtube_search",
                        "query": query,
                    }
                ],
            )

            return

        # -------------------------------------------------
        # Google
        # -------------------------------------------------

        if current_site == "google":

            print(
                "[ACTION MEMORY] "
                "Google Search"
            )

            task_manager.start(
                "executor",
                execute_ai_plan,
                [
                    {
                        "action": "google_search",
                        "query": query,
                    }
                ],
            )

            return

    # =====================================================
    # EXISTING CHAT / PLANNER
    # =====================================================

    mode = detect(
        command
    )

    # -----------------------------------------------------
    # Continue conversation
    # -----------------------------------------------------

    if get_value(
        "chat_mode"
    ):

        mode = "chat"

    # -----------------------------------------------------
    # Chat
    # -----------------------------------------------------

    if mode == "chat":

        task_manager.start(
            "chat",
            chat_worker,
            command,
        )

    # -----------------------------------------------------
    # Planner
    # -----------------------------------------------------

    else:

        task_manager.start(
            "planner",
            planner_worker,
            command,
        )