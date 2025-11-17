import random

FRIENDLY_LINES = [
    "Proud of you for checking in today 🌱",
    "One step at a time — you’re doing great 💪",
    "Consistency beats perfection — every time ✨",
    "Showing up today is already a win 🤍",
]

def add_warmth(text):
    return text + "\n\n" + random.choice(FRIENDLY_LINES)
