# ============================================================
# eval_set.py  -  the ANSWER KEY for the scorecard (the "exam paper").
# Each question has:
#   question : what we ask the bot (some are deliberately worded differently from the PDF)
#   evidence : a phrase that MUST appear in the retrieved chunks, or the search failed (None = unanswerable)
#   answers  : the answer is correct if it contains ANY of these (lowercase). ["don't know"] = should refuse.
# ============================================================

QUESTIONS = [
    {"question": "How much does student membership cost per year?", "evidence": "250 rupees per year", "answers": ["250"]},
    {"question": "Do senior citizens have to pay for membership?", "evidence": "free membership", "answers": ["free", "no"]},
    {"question": "How many books can I borrow at one time?", "evidence": "up to 5 books", "answers": ["5 books", "five books", "up to 5", "5"]},
    {"question": "For how many days can I keep a magazine?", "evidence": "Magazines can be borrowed for 7 days", "answers": ["7 days", "seven days", "7"]},
    {"question": "What is the overdue charge per day for a book?", "evidence": "2 rupees per day", "answers": ["2 rupees", "2 rupee", "rs 2", "₹2"]},
    {"question": "I returned a book 60 days late. How much is the late fee?", "evidence": "up to a maximum of 100 rupees", "answers": ["100"]},
    {"question": "What do I pay if I lose a book?", "evidence": "printed price", "answers": ["printed price"]},
    {"question": "What time does the library open on Sunday?", "evidence": "Sunday from 10 AM to 2 PM", "answers": ["10 am", "10:00 am", "10am", "10 a.m."]},
    {"question": "Until what time is the library open on weekdays during exam season?", "evidence": "until 10 PM on weekdays", "answers": ["10 pm", "10:00 pm", "10pm", "10 p.m."]},
    {"question": "How many computers are in the computer lab?", "evidence": "20 computers", "answers": ["20"]},
    {"question": "How many people fit in a study room?", "evidence": "seat up to 6 people", "answers": ["6", "six"]},
    {"question": "Who is in charge of the library?", "evidence": "Anita Rao", "answers": ["anita rao"]},
    {"question": "What is the front desk phone number?", "evidence": "0253 555 0142", "answers": ["0253 555 0142", "0253-555-0142", "02535550142"]},
    {"question": "How long can I borrow an e-book?", "evidence": "3 e-books at a time for 21 days", "answers": ["21 days", "21"]},
    {"question": "How do I sign in to the digital library app?", "evidence": "4 digit PIN", "answers": ["pin"]},
    {"question": "How much does a colour printout cost per page?", "evidence": "5 rupees per colour page", "answers": ["5 rupees", "5 rupee", "rs 5", "₹5"]},
    {"question": "When does the book club meet?", "evidence": "first Thursday of each month at 6 PM", "answers": ["first thursday"]},
    {"question": "How many books can I donate in one visit?", "evidence": "up to 20 books per visit", "answers": ["20"]},
    {"question": "What time does the cafe close?", "evidence": "9:30 AM to 6:30 PM", "answers": ["6:30", "6.30", "6:30 pm"]},
    {"question": "Where is the wheelchair ramp?", "evidence": "north entrance", "answers": ["north"]},
    {"question": "How long does an inter-library loan take?", "evidence": "7 to 10 working days", "answers": ["7 to 10", "7-10", "7–10", "seven to ten"]},
    {"question": "How many books can I reserve at once?", "evidence": "reserve up to 3 books", "answers": ["3 books", "three books", "up to 3", "3"]},
    {"question": "How long is a reserved book held for me?", "evidence": "held at the desk for 3 days", "answers": ["3 days", "three days"]},
    {"question": "Does the library have a swimming pool?", "evidence": None, "answers": ["don't know"]},
    {"question": "What is the library's yearly budget?", "evidence": None, "answers": ["don't know"]},
]
