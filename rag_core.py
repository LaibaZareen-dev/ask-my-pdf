# ============================================================
# rag_core.py  -  the "engine room": all the RAG functions live here.
# Both the chat page (app.py) and the scorecard page import from this file,
# so the logic is written ONCE. (Analogy: one kitchen serving two dining rooms.)
# ============================================================

import streamlit as st  # used only to read st.secrets (where your API key is saved)
from pypdf import PdfReader  # reads the text out of a PDF file
from sklearn.feature_extraction.text import TfidfVectorizer  # turns text into "importance of each letter-group" numbers
from sklearn.metrics.pairwise import cosine_similarity  # measures how close two sets of numbers are
from google import genai  # official Gemini API client

GEMINI_MODEL = "gemini-3.5-flash-lite"  # ONE place to change the model name if Google retires it or you hit a quota


def find_saved_key() -> str:
    """Looks for your Gemini key in Streamlit's secrets under a few possible names."""
    for key_name in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GOOGLE_API_KEY", "GOOGLE_API_KEY_2"):  # names we accept
        try:
            if key_name in st.secrets:  # is a secret with this name saved?
                return str(st.secrets[key_name]).strip()  # return it, trimmed of stray spaces
        except Exception:  # raised when there is no secrets file at all (e.g. first local run)
            return ""  # no secrets available
    return ""  # none of the names were found


def extract_text(pdf_file) -> str:
    """Takes a PDF (uploaded file or a file path) and returns all its text as one long string."""
    reader = PdfReader(pdf_file)  # opens the PDF and finds its pages
    pages_text = []  # empty list, we'll add each page's text into it
    for page in reader.pages:  # loop over every page, one at a time
        text = page.extract_text() or ""  # pull the text out; "or ''" guards against a blank/image page
        pages_text.append(" ".join(text.split()))  # collapse newlines/extra spaces into single spaces
    return " ".join(pages_text)  # join all pages into one string


def make_chunks(full_text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Cuts one long string into overlapping chunks (our 'index cards'), never cutting a word in half."""
    chunks = []  # the finished cards
    start = 0  # where the next card begins, in characters
    text_length = len(full_text)  # total characters in the PDF text
    while start < text_length:  # keep going until the whole text is covered
        end = start + chunk_size  # ideal end of this card
        if end < text_length:  # only snap to a space if we're not at the very end
            while end > start and full_text[end] != " ":  # walk left until we hit a space
                end -= 1  # step back one character
        chunk = full_text[start:end].strip()  # slice out the card
        if chunk:  # skip empty cards
            chunks.append(chunk)  # add it to the stack
        if end >= text_length:  # we just wrote the final card, so stop (prevents a tiny duplicate card)
            break
        start = max(end - overlap, start + 1)  # step back by `overlap` for the next card, but always move forward
        while start < text_length and full_text[start] != " " and start > 0 and full_text[start - 1] != " ":
            start += 1  # move forward to the start of a whole word
    return chunks  # the full stack of index cards


def build_search_index(chunks: list[str]):
    """One-time setup after upload: score every chunk with TF-IDF."""
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",  # compare small letter-groups, so "resource" matches "resources"
        ngram_range=(3, 5),  # letter-groups 3 to 5 letters long
        sublinear_tf=True,  # stops a repeated word from dominating the score
    )
    chunk_vectors = vectorizer.fit_transform(chunks)  # learn the letter-groups AND score every chunk
    return vectorizer, chunk_vectors  # keep both: questions must be scored the same way


def find_best_chunks(question: str, chunks: list[str], vectorizer, chunk_vectors, top_k: int = 5) -> list[str]:
    """Runs on every question: returns the top_k chunks closest to it."""
    question_vector = vectorizer.transform([question])  # score the question with the SAME letter-groups
    scores = cosine_similarity(question_vector, chunk_vectors)[0]  # one similarity score per chunk
    top_indices = scores.argsort()[::-1][:top_k]  # highest scores first, keep top_k
    return [chunks[i] for i in top_indices]  # fetch the chunk texts


def ask_gemini(question: str, context_chunks: list[str], api_key: str) -> str:
    """Sends the question + retrieved chunks to Gemini and returns its answer."""
    client = genai.Client(api_key=api_key)  # connect to Gemini
    numbered_cards = "\n\n".join(f"Card {i+1}: {c}" for i, c in enumerate(context_chunks))  # "Card 1: ...", "Card 2: ..."
    prompt = (
        "You are a helpful assistant that answers ONLY using the cards below, which are excerpts "
        "from a document. If the answer is not contained in the cards, reply exactly: "
        "\"I don't know — that isn't in this document.\" Do not use outside knowledge. "
        "If the cards contain links (URLs) that answer the question, list them in full. "
        "You may do simple arithmetic with numbers found in the cards to answer calculation questions, "
        "and you should apply any maximum or cap the cards mention. Keep answers short.\n\n"
        f"{numbered_cards}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)  # the actual API call
    return response.text  # Gemini's answer as plain text
