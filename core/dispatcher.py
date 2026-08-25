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
from brain.execution_context import execution_context_resolver

from brain.followup_execution_bridge import (
    followup_execution_bridge,
)

# =========================================================
# DISPATCHER
# =========================================================

def dispatch(
    command,
    skip_fast=False,
    fast_plan=None,
    conversation_request=None,
):

    command = command.strip()

    if not command:
        return
    
    
    # =====================================================
    # LIVE CONVERSATION CONTROL
    # =====================================================

    live_command = command.lower().strip()

    if live_command in {
        "start live conversation",
        "start live mode",
        "enter live conversation",
        "start natural live conversation",
    }:

        return execute(
            "start_live_conversation"
        )

    if live_command in {
        "stop live conversation",
        "stop live mode",
        "exit live conversation",
        "end live conversation",
    }:

        return execute(
            "stop_live_conversation"
        )

    if live_command in {
        "live conversation status",
        "live mode status",
    }:

        return execute(
            "live_conversation_status"
        )

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
    # NATURAL CONVERSATION ANALYSIS
    # =====================================================
    #
    # ConversationRequest is now the preferred common
    # conversational interface.
    #
    # During migration, the existing ConversationCoordinator
    # remains as a compatibility fallback.
    #
    # IMPORTANT:
    # This section only prepares conversational information.
    # It does not execute anything.
    # =====================================================

    conversation_analysis = None

    try:

        if conversation_request is not None:

            from brain.followup_resolver import (
                FollowUpResolution,
            )

            # -------------------------------------------------
            # Adapt the new common ConversationRequest into
            # the existing FollowUpResolution interface.
            #
            # This allows the existing FollowUpExecutionBridge
            # to remain unchanged during the migration.
            # -------------------------------------------------

            conversation_analysis = type(
                "ConversationAnalysisAdapter",
                (),
                {}
            )()

            conversation_analysis.follow_up = (
                FollowUpResolution(

                    is_follow_up=(
                        conversation_request.relation
                        in {
                            "follow_up",
                            "continuation",
                            "correction",
                            "reference",
                            "contextual_reference",
                        }
                        or conversation_request.intent
                        == "contextual_reference"
                    ),

                    raw_input=(
                        conversation_request.user_input
                        or command
                    ),

                    relation=(
                        conversation_request.relation
                    ),

                    application=(
                        conversation_request.application
                    ),

                    skill=(
                        conversation_request.skill
                    ),

                    topic=(
                        conversation_request.topic
                    ),

                    task=(
                        conversation_request.task
                    ),

                    intent=(
                        conversation_request.intent
                    ),

                    action=(
                        conversation_request.action
                    ),

                    object=(
                        conversation_request.object
                    ),

                    references=list(
                        conversation_request.references
                        or []
                    ),

                    resolved_references=dict(
                        conversation_request
                        .resolved_references
                        or {}
                    ),

                    unresolved_references=list(
                        conversation_request
                        .unresolved_references
                        or []
                    ),

                    confidence=(
                        conversation_request.confidence
                    ),

                    reason=(
                        "Adapted from ConversationRequest."
                    ),
                )
            )

            print(
                "[CONVERSATION] "
                "Using ConversationRequest."
            )

        else:

            # -------------------------------------------------
            # Compatibility fallback
            # -------------------------------------------------

            conversation_analysis = (
                conversation_coordinator.analyze(
                    command
                )
            )

            print(
                "[CONVERSATION] "
                "Using ConversationCoordinator fallback."
            )

    except Exception as e:

        print(
            "[CONVERSATION] "
            f"Analysis failed safely: {e}"
        )
        
    # =====================================================
    # NATURAL CONVERSATION FOLLOW-UP PRIORITY
    # =====================================================
    #
    # If NCI has a valid contextual follow-up, let the
    # Follow-Up Execution Bridge handle it before FAST ROUTE.
    #
    # This prevents generic fast commands from stealing
    # context-sensitive commands such as:
    #
    #     YouTube → "play the next one"
    #     YouTube → "play the first one"
    #
    # Normal commands still continue to FAST ROUTE.
    # =====================================================

    if (
        not skip_fast
        and conversation_analysis is not None
        and conversation_analysis.follow_up is not None
        and conversation_analysis.follow_up.is_follow_up
    ):

        follow_up_plan = (
            followup_execution_bridge.resolve(
                raw_input=command,
                follow_up=(
                    conversation_analysis.follow_up
                ),
            )
        )

        if follow_up_plan:

            print(
                "[CONVERSATION PRIORITY] "
                "Contextual follow-up takes priority:",
                follow_up_plan,
            )

            for action in follow_up_plan:

                action_name = action.get(
                    "action"
                )

                if not action_name:
                    continue

                print(
                    "[CONVERSATION PRIORITY] "
                    f"Executing {action_name}"
                )

                result = execute(
                    action_name,
                    action,
                )

                print(
                    "[CONVERSATION PRIORITY RESULT]",
                    repr(result),
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
                #
                # Convert the already-executed action into
                # semantic conversational context.
                #
                # This does NOT execute anything.
                # =========================================

                try:

                    execution_context = (
                        execution_context_resolver.resolve(

                            action_name=action_name,

                            action_data=action,

                            result=result,

                        )
                    )

                    conversation_coordinator.record_execution(

                        topic=execution_context.topic,

                        task=execution_context.task,

                        application=(
                            execution_context.application
                        ),

                        skill=execution_context.skill,

                        intent=execution_context.intent,

                        action=execution_context.action,

                        object=execution_context.object,

                        objects=execution_context.objects,

                        result=result,

                    )

                    print(
                        "[CONVERSATION EXECUTION]",
                        conversation_coordinator.context.snapshot(),
                    )

                except Exception as e:

                    # -------------------------------------
                    # Natural Conversation must NEVER
                    # break existing JARVIS execution.
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
    # CONTEXT-AWARE GENERIC SEARCH
    # =====================================================
    #
    # If the user previously selected a search platform,
    # a natural "search ..." continuation should inherit
    # that platform.
    #
    # Example:
    #
    #   Open YouTube
    #   Search ESP32 weather station
    #
    # becomes:
    #
    #   youtube_search("ESP32 weather station")
    #
    # This is shared by voice and Remote Control because
    # both use the same dispatcher and action memory.
    # =====================================================

    if (
        not skip_fast
        and command.lower().startswith("search ")
        and "youtube" not in command.lower()
        and "google" not in command.lower()
        and "github" not in command.lower()
        and "chatgpt" not in command.lower()
    ):

        current_site = get_memory(
            "site"
        )

        query = command[
            len("search "):
        ].strip()

        if query:

            # -------------------------------------------------
            # YouTube context
            # -------------------------------------------------

            if current_site == "youtube":

                print(
                    "[ACTION MEMORY] "
                    "Context resolved: YouTube"
                )

                print(
                    "[ACTION MEMORY] "
                    f"YouTube Search: {query}"
                )

                result = execute(
                    "youtube_search",
                    {
                        "action":
                            "youtube_search",
                        "query":
                            query,
                    },
                )

                print(
                    "[ACTION MEMORY RESULT]",
                    repr(result),
                )

                return

            # -------------------------------------------------
            # Google context
            # -------------------------------------------------

            if current_site == "google":

                print(
                    "[ACTION MEMORY] "
                    "Context resolved: Google"
                )

                print(
                    "[ACTION MEMORY] "
                    f"Google Search: {query}"
                )

                result = execute(
                    "google_search",
                    {
                        "action":
                            "google_search",
                        "query":
                            query,
                    },
                )

                print(
                    "[ACTION MEMORY RESULT]",
                    repr(result),
                )

                return

            # -------------------------------------------------
            # GitHub context
            # -------------------------------------------------

            if current_site == "github":

                print(
                    "[ACTION MEMORY] "
                    "Context resolved: GitHub"
                )

                print(
                    "[ACTION MEMORY] "
                    f"GitHub Search: {query}"
                )

                result = execute(
                    "github_search",
                    {
                        "action":
                            "github_search",
                        "query":
                            query,
                    },
                )

                print(
                    "[ACTION MEMORY RESULT]",
                    repr(result),
                )

                return

    # =====================================================
    # NATURAL CONVERSATION FOLLOW-UP EXECUTION
    # =====================================================
    #
    # Fast routing has already been given priority.
    #
    # The conversation analysis was already performed
    # BEFORE FAST ROUTE.
    #
    # We reuse that analysis here.
    #
    # Natural Conversation does NOT execute directly.
    # The normal registry executor remains authoritative.
    # =====================================================

    try:

        # -------------------------------------------------
        # Reuse existing conversation analysis
        # -------------------------------------------------

        if conversation_analysis is not None:

            follow_up = (
                conversation_analysis.follow_up
            )

            follow_up_plan = (
                followup_execution_bridge.resolve(

                    raw_input=command,

                    follow_up=follow_up,

                )
            )

        else:

            follow_up_plan = None

        # -------------------------------------------------
        # Execute resolved follow-up
        # -------------------------------------------------

        if follow_up_plan:

            print(
                "[CONVERSATION FOLLOW-UP] "
                "Execution plan:",
                follow_up_plan,
            )

            for action in follow_up_plan:

                action_name = action.get(
                    "action"
                )

                if not action_name:
                    continue

                print(
                    "[CONVERSATION FOLLOW-UP] "
                    f"Executing {action_name}"
                )

                result = execute(
                    action_name,
                    action,
                )

                print(
                    "[CONVERSATION FOLLOW-UP RESULT]",
                    repr(result),
                )

                # -----------------------------------------
                # Update conversational context
                # -----------------------------------------

                try:

                    execution_context = (
                        execution_context_resolver.resolve(

                            action_name=action_name,

                            action_data=action,

                            result=result,

                        )
                    )

                    conversation_coordinator.record_execution(

                        topic=execution_context.topic,

                        task=execution_context.task,

                        application=(
                            execution_context.application
                        ),

                        skill=execution_context.skill,

                        intent=execution_context.intent,

                        action=execution_context.action,

                        object=execution_context.object,

                        objects=execution_context.objects,

                        result=result,

                    )

                    print(
                        "[CONVERSATION EXECUTION]",
                        conversation_coordinator.context.snapshot(),
                    )

                except Exception as e:

                    print(
                        "[CONVERSATION] "
                        f"Follow-up context update failed: {e}"
                    )

            return

    except Exception as e:

        # -------------------------------------------------
        # Natural Conversation must NEVER break JARVIS.
        # -------------------------------------------------

        print(
            "[CONVERSATION] "
            f"Follow-up execution failed safely: {e}"
        )

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
    
    # # =====================================================
    # # GENERIC SEARCH USING ACTION MEMORY
    # # =====================================================

    # if (
    #     command.startswith("search ")
    #     and "youtube" not in command
    #     and "google" not in command
    #     and "github" not in command
    #     and "chatgpt" not in command
    # ):

    #     current_site = get_memory(
    #         "site"
    #     )

    #     query = (
    #         command
    #         .replace(
    #             "search",
    #             "",
    #             1,
    #         )
    #         .strip()
    #     )

    #     # -------------------------------------------------
    #     # YouTube
    #     # -------------------------------------------------

    #     if current_site == "youtube":

    #         print(
    #             "[ACTION MEMORY] "
    #             "YouTube Search"
    #         )

    #         result = execute(
    #             "youtube_search",
    #             {
    #                 "action": "youtube_search",
    #                 "query": query,
    #             },
    #         )

    #         print(
    #             "[ACTION MEMORY RESULT]",
    #             repr(result),
    #         )

    #         return

    #     # -------------------------------------------------
    #     # Google
    #     # -------------------------------------------------

    #     if current_site == "google":

    #         print(
    #             "[ACTION MEMORY] "
    #             "Google Search"
    #         )

    #         task_manager.start(
    #             "executor",
    #             execute_ai_plan,
    #             [
    #                 {
    #                     "action": "google_search",
    #                     "query": query,
    #                 }
    #             ],
    #         )

    #         return

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