import spacy
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Spoken number → digit mapping
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12
}

EVENT_TYPES = {
    "meeting": ["meeting", "review", "planning", "status", "client", "interview"],
    "announcement": ["announcement", "notify", "release", "publish"],
    "training": ["training", "workshop", "session", "webinar"],
    "call": ["call", "conference"]
}

# IMPORTANT: generic words last
TEAM_KEYWORDS = ["development team","marketing team","hr team","design team","project team","team members"]


def detect_event_type(text):
    text = text.lower()
    for event_type, keywords in EVENT_TYPES.items():
        for kw in keywords:
            if kw in text:
                return event_type
    return "general"


def extract_event_details(text):
    doc = nlp(text)
    event_type = detect_event_type(text)

    subject_map = {
        "meeting": "General Meeting",
        "announcement": "Team Announcement",
        "training": "Training Session",
        "call": "Conference Call",
        "general": "General Information"
    }

    date = "Not mentioned"
    time = "Not mentioned"
    participants = []
    platform = "Not mentioned"

    text_lower = text.lower()

    # -------- 1️⃣ spaCy Entity Extraction --------
    for ent in doc.ents:
        if ent.label_ == "DATE" and date == "Not mentioned":
            date = ent.text

        elif ent.label_ == "TIME" and time == "Not mentioned":
            time = ent.text

        elif ent.label_ == "PERSON":
            participants.append(ent.text)

        elif ent.label_ == "ORG":
            # Skip platform names
            if ent.text.lower() not in ["google meet", "microsoft teams", "zoom"]:
                participants.append(ent.text)

    # -------- 2️⃣ Team Phrase Detection (NO DUPLICATES) --------
    for team in TEAM_KEYWORDS:
        if team in text_lower:
            participants.append(team.title())
            break   # stop after first meaningful match

    # -------- 3️⃣ Regex name list (John, Priya, Arun) --------
    name_pattern = r'with\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*(?:\s+and\s+[A-Z][a-z]+)?)'
    match = re.search(name_pattern, text)
    if match:
        participants.append(match.group(1))

    # -------- 4️⃣ Normalize Participants --------
    if participants:
        participants = ", ".join(sorted(set(participants)))
    else:
        participants = "Not mentioned"

    # -------- 5️⃣ Numeric Time --------
    time_pattern = r'\b(\d{1,2}(:\d{2})?\s?(a\.?m\.?|p\.?m\.?))\b'
    match = re.search(time_pattern, text_lower)

    if match:
        clean_time = match.group(1)
        clean_time = clean_time.replace(".", "")
        clean_time = clean_time.upper()
        time = clean_time

    # -------- 6️⃣ Spoken Time --------
    time_lower = time.lower()
    for word, hour in NUMBER_WORDS.items():
        if word in time_lower and "o'clock" in time_lower:
            meridian = "PM" if any(x in time_lower for x in ["evening", "night", "afternoon"]) else "AM"
            time = f"{hour}:00 {meridian}"
            break

    # -------- 7️⃣ Platform Detection --------
    if "zoom" in text_lower:
        platform = "Zoom"
    elif "google meet" in text_lower:
        platform = "Google Meet"
    elif "teams" in text_lower:
        platform = "Microsoft Teams"

    return {
        "event_type": event_type,
        "subject": subject_map[event_type],
        "date": date,
        "time": time,
        "agenda": subject_map[event_type],
        "participants": participants,
        "platform": platform
    }
