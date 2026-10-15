# ============================================================
# pages/Scorecard.py  -  the exam hall.
# Asks the bot 25 questions whose answers we already know, then counts how many it got right.
# We score TWO things separately:
#   1) Retrieval  = did the search hand the AI the card that contains the answer?
#   2) Answer     = did the AI's final answer contain the correct fact?
# If retrieval fails, the AI never had a chance. If retrieval passes but the answer fails, the AI messed up.
# ============================================================

import time  # for pausing between questions so we stay under the free-tier rate limit
import pandas as pd  # tables (comes with Streamlit, no extra install)
import streamlit as st  # the web page tools
from rag_core import extract_text, make_chunks, build_search_index, find_best_chunks, ask_gemini, find_saved_key
from eval_set import QUESTIONS  # the answer key

st.set_page_config(page_title="Scorecard - Ask My PDF", page_icon="📊", layout="wide")  # tab title and icon
st.title("Scorecard")  # page heading
st.write(
    "25 questions with a known answer key, asked about the built-in sample handbook. "
    "Change the settings, run again, and compare the scores."
)  # one-line explanation for visitors

# ---------- helper: tidy text before comparing ----------
def normalise(text: str) -> str:
    """Lowercase and unify fancy quotes/dashes/commas so 'don’t' matches "don't"."""
    text = text.lower().replace("’", "'").replace("–", "-").replace(",", "")  # unify punctuation
    return " ".join(text.split())  # collapse extra spaces

# ---------- settings ----------
col1, col2 = st.columns(2)  # two side-by-side controls
with col1:
    chunk_size = st.select_slider("Chunk size (characters per card)", options=[200, 400, 800], value=400)  # card size
with col2:
    top_k = st.slider("Cards sent to the AI (top-k)", 1, 8, 3)  # how many cards are retrieved per question

api_key = find_saved_key()  # try the saved secret first
if not api_key:  # no saved key, so allow typing one
    api_key = st.text_input("Gemini API key (only needed for the full scorecard)", type="password")

if "runs" not in st.session_state:  # first visit to this page in this session
    st.session_state["runs"] = []  # list of finished runs

# ---------- the exam ----------
def run_scorecard(use_ai: bool):
    """Runs all questions with the chosen settings and stores the result."""
    text = extract_text("sample.pdf")  # read the sample handbook
    chunks = make_chunks(text, chunk_size=chunk_size, overlap=min(150, chunk_size // 3))  # cut it into cards
    vectorizer, chunk_vectors = build_search_index(chunks)  # score the cards once
    rows = []  # one row per question
    bar = st.progress(0.0, text="Starting...")  # progress bar
    for n, q in enumerate(QUESTIONS, start=1):  # go through the questions one by one
        top = find_best_chunks(q["question"], chunks, vectorizer, chunk_vectors, top_k=top_k)  # step 1: retrieve
        joined = normalise(" ".join(top))  # all retrieved text, tidied
        if q["evidence"] is None:  # unanswerable question: retrieval can't "hit"
            retrieval_ok = None
        else:
            retrieval_ok = normalise(q["evidence"]) in joined  # was the key phrase in the retrieved cards?
        answer, answer_ok = "", None  # defaults when we skip the AI
        if use_ai:  # step 2: ask Gemini
            for attempt in range(2):  # try twice (the second try helps with a temporary rate limit)
                try:
                    answer = ask_gemini(q["question"], top, api_key)  # the real call
                    break  # success, stop retrying
                except Exception as error:
                    answer = f"ERROR: {error}"  # remember what went wrong
                    time.sleep(20)  # wait before the second try
            answer_ok = any(normalise(a) in normalise(answer) for a in q["answers"])  # does it contain a correct answer?
            time.sleep(4)  # pause so we stay under the free-tier per-minute limit
        rows.append({
            "#": n, "Question": q["question"],
            "Retrieval": "n/a" if retrieval_ok is None else ("✅" if retrieval_ok else "❌"),
            "Answer": "—" if answer_ok is None else ("✅" if answer_ok else "❌"),
            "Bot said": answer[:160],
            "_r": retrieval_ok, "_a": answer_ok,
        })
        bar.progress(n / len(QUESTIONS), text=f"Question {n} of {len(QUESTIONS)}")  # update the bar
    bar.empty()  # remove the bar
    answerable = [r for r in rows if r["_r"] is not None]  # questions that have an answer in the PDF
    st.session_state["runs"].append({
        "Settings": f"chunk {chunk_size}, top-k {top_k}" + ("" if use_ai else " (retrieval only)"),
        "Chunks": len(chunks),
        "Retrieval": f"{sum(r['_r'] for r in answerable)}/{len(answerable)}",
        "Answers": f"{sum(bool(r['_a']) for r in rows)}/{len(rows)}" if use_ai else "—",
        "rows": rows,
    })

b1, b2 = st.columns(2)  # two buttons
if b1.button("Run retrieval check (instant, no AI calls)"):
    run_scorecard(use_ai=False)
if b2.button("Run full scorecard (about 2 minutes, uses Gemini)", disabled=not api_key):
    run_scorecard(use_ai=True)

# ---------- results ----------
if st.session_state["runs"]:
    st.subheader("Runs so far")  # comparison table across runs
    st.dataframe(
        pd.DataFrame([{k: v for k, v in r.items() if k != "rows"} for r in st.session_state["runs"]]),
        hide_index=True, width="stretch",
    )
    st.subheader("Latest run: question by question")  # detail of the most recent run
    latest = pd.DataFrame(st.session_state["runs"][-1]["rows"]).drop(columns=["_r", "_a"])
    st.dataframe(latest, hide_index=True, width="stretch")
    st.caption("Retrieval ❌ means the search missed the right card, so the AI had no chance. "
               "Retrieval ✅ with Answer ❌ means the AI had the right card but answered badly.")
