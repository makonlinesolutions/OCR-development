from fuzzywuzzy import fuzz, process

KNOWN_NAMES = [
    "ONKAR DATTATRAYA KULKARNI",
    "DATTATRAYA BHAGWAN KULKARNI",
    "RAHUL KUMAR",
    "PRACHI ONKAR KULKARNI",
    "RAM NATH",
    "AJAY KUMAR"
]

def fuzzy_correct_name(name: str, choices=KNOWN_NAMES, threshold=85):
    if not name:
        return None
    match, score = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
    return match if score >= threshold else name
