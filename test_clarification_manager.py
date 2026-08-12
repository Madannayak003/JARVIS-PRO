from brain.clarification_manager import (
    ClarificationManager
)


manager = ClarificationManager()


# ============================================================
# TEST 1 — Empty
# ============================================================

print("\n[TEST 1] Empty")

print(
    manager.info()
)


# ============================================================
# TEST 2 — Start clarification
# ============================================================

print("\n[TEST 2] Start clarification")

manager.start(
    field="search_platform",
    question="Which platform should I search?",
    task="search for Python tutorials",
    owner="browser",
    metadata={
        "pending_search": "Python tutorials"
    }
)

print(
    manager.info()
)


# ============================================================
# TEST 3 — Waiting
# ============================================================

print("\n[TEST 3] Waiting")

print(
    manager.is_waiting()
)

print(
    "Field:",
    manager.field()
)

print(
    "Question:",
    manager.question()
)


# ============================================================
# TEST 4 — Resolve
# ============================================================

print("\n[TEST 4] Resolve")

result = manager.resolve(
    "google"
)

print(
    result
)


# ============================================================
# TEST 5 — Confirm cleared
# ============================================================

print("\n[TEST 5] After resolve")

print(
    manager.info()
)

print(
    "Waiting:",
    manager.is_waiting()
)


# ============================================================
# TEST 6 — WhatsApp-style clarification
# ============================================================

print("\n[TEST 6] WhatsApp clarification")

manager.start(
    field="recipient",
    question="Who should I send the message to?",
    task="send WhatsApp message",
    owner="whatsapp"
)

print(
    manager.info()
)

result = manager.resolve(
    "Rahul"
)

print(
    "Resolved:",
    result
)


# ============================================================
# TEST 7 — Clear
# ============================================================

print("\n[TEST 7] Clear")

manager.start(
    field="message",
    question="What message should I send?",
    task="send WhatsApp message",
    owner="whatsapp"
)

print(
    "Before:",
    manager.info()
)

manager.clear()

print(
    "After:",
    manager.info()
)