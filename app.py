# ============================================================
# Ask My PDF  -  Step 0: the page shell (no AI yet)
# Analogy: today we build the SHOP FRONT. Next steps add the kitchen (the RAG part).
# ============================================================

import streamlit as st  # Streamlit = turns Python code into a web page, no HTML server needed
from pypdf import PdfReader  # pypdf = reads the text out of a PDF file, page by page

# ---------- 1. Page settings (must be the FIRST Streamlit command) ----------
st.set_page_config(  # tells the browser how to show our page
    page_title="Ask My PDF",  # text shown on the browser tab
    page_icon="📄",  # small icon shown on the browser tab
    layout="wide",  # use the full width of the screen
    initial_sidebar_state="expanded",  # keep the left sidebar open when the page loads
)  # end of page settings

# ---------- 2. Styling (plain CSS, which you already know) ----------
# We store the CSS in a Python string, then send it to the page in step 3.
STYLE = """
<style>
/* Load two Google fonts: Bricolage Grotesque for headings, DM Sans for body text */
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* Colour variables. Change a colour here and it changes everywhere. */
:root {
  --navy: #1B2A4A;   /* deep ink blue: hero background and main text */
  --paper: #FFFEFA;  /* index-card white */
  --rule: #C9D8F0;   /* light blue ruled lines, like an index card */
  --red: #D64550;    /* the red top line on index cards */
  --muted: #5B6B86;  /* softer text colour for descriptions */
}

/* Page body font, and a tidier page width */
.stApp { font-family: 'DM Sans', sans-serif; }
.stApp .block-container { max-width: 1100px; padding-top: 2.2rem; }

/* Hide Streamlit's default footer so the page looks like our own product */
footer { visibility: hidden; }

/* Hero: a big navy panel, text on the left and index cards on the right */
.stApp .hero {
  display: grid;                      /* two columns */
  grid-template-columns: 1.15fr 1fr;  /* left column a bit wider */
  gap: 2.5rem;                        /* space between the columns */
  align-items: center;                /* centre both columns vertically */
  background: var(--navy);
  color: #fff;
  border-radius: 20px;
  padding: 3rem;
}
.stApp .hero h1 {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: clamp(2rem, 4.2vw, 3.2rem);  /* shrinks on small screens */
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  margin: 0 0 1rem 0;
  padding: 0;
}
.stApp .hero p {
  color: #C9D6EE;
  font-size: 1.08rem;
  line-height: 1.55;
  max-width: 46ch;  /* keeps lines short and easy to read */
  margin: 0;
}

/* Small status pill with a green dot (a green dot means "live") */
.stApp .chip {
  display: inline-block;
  margin-top: 1.4rem;
  padding: .45rem .9rem;
  border-radius: 999px;
  background: #2C406B;
  color: #fff;
  font-size: .9rem;
}
.stApp .chip::before {
  content: "";
  display: inline-block;
  width: 8px; height: 8px;
  margin-right: .55rem;
  border-radius: 50%;
  background: #6FD3A0;
}

/* The stack of two tilted index cards in the hero */
.stApp .stack { position: relative; height: 260px; }
.stApp .card {
  position: absolute;
  width: 80%;
  background-color: var(--paper);
  /* the blue ruled lines of an index card */
  background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 27px, var(--rule) 27px, var(--rule) 28px);
  border-top: 4px solid var(--red);  /* red top line */
  border-radius: 6px;
  padding: 1rem 1.2rem;
  color: var(--navy);
  font-size: .98rem;
  line-height: 28px;  /* same as the ruled-line spacing so text sits on the lines */
  box-shadow: 0 8px 18px rgba(8, 16, 40, .35);
}
.stApp .card small { display: block; color: var(--muted); font-size: .82rem; }
.stApp .card-back  { top: 0;    left: 0;  transform: rotate(-3deg); }
.stApp .card-front { bottom: 0; right: 0; transform: rotate(2deg); }

/* "How it works" heading */
.stApp h2.how {
  font-family: 'Bricolage Grotesque', sans-serif;
  color: var(--navy);
  margin: 2.4rem 0 1rem 0;
  padding: 0;
}

/* Four step cards. Numbered because they really are a sequence. */
.stApp .steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.stApp .step {
  background: var(--paper);
  border-top: 4px solid var(--red);
  border-radius: 6px;
  padding: 1rem 1.1rem 1.3rem 1.1rem;
  color: var(--navy);
}
.stApp .step .num { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.6rem; color: var(--red); }
.stApp .step h3 {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-size: 1.1rem;
  color: var(--navy);
  margin: .2rem 0 .4rem 0;
  padding: 0;
}
.stApp .step p { margin: 0; color: var(--muted); font-size: .95rem; line-height: 1.45; }

/* Sidebar: a thin line to separate it from the page */
section[data-testid="stSidebar"] { border-right: 1px solid var(--rule); }

/* Phones and small screens: stack columns */
@media (max-width: 800px) {
  .stApp .hero { grid-template-columns: 1fr; padding: 2rem 1.4rem; }
  .stApp .steps { grid-template-columns: 1fr 1fr; }
}
</style>
"""  # end of the CSS string

# ---------- 3. Send the CSS to the page ----------
st.markdown(STYLE, unsafe_allow_html=True)  # unsafe_allow_html=True means "yes, treat this as real HTML/CSS"


# ---------- 3b. Helper functions: read the PDF, then cut it into chunks ----------
def extract_text(pdf_file) -> str:
    """Takes the uploaded PDF and returns all its text as one long string."""
    reader = PdfReader(pdf_file)  # opens the PDF and finds its pages
    pages_text = []  # empty list, we'll add each page's text into it
    for page in reader.pages:  # loop over every page in the PDF, one at a time
        text = page.extract_text() or ""  # pull the text out; "or ''" guards against a blank/image page
        pages_text.append(text)  # add this page's text to our list
    return "\n".join(pages_text)  # join all pages into one string, separated by newlines


def make_chunks(full_text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Cuts one long string into overlapping chunks (our 'index cards').

    chunk_size = how many characters go on one card (roughly 120-150 words).
    overlap    = characters repeated from the end of one card to the start of the
                 next, so a sentence that got cut in half isn't lost between cards.
    """
    chunks = []  # empty list to collect the finished cards
    start = 0  # where the next card begins, in characters
    text_length = len(full_text)  # total number of characters in the whole PDF text
    while start < text_length:  # keep going until we've covered the whole text
        end = start + chunk_size  # where this card ends
        chunk = full_text[start:end].strip()  # slice out the card's text; strip() removes stray spaces
        if chunk:  # skip empty cards (can happen near blank pages)
            chunks.append(chunk)  # add this card to our list
        start = end - overlap  # move forward, but step back a bit so cards overlap
    return chunks  # the full stack of index cards


# ---------- 4. Sidebar (left panel): where the user uploads their PDF ----------
with st.sidebar:  # everything indented under this line appears in the sidebar
    st.subheader("Your document")  # small heading
    uploaded_pdf = st.file_uploader(  # draws an upload box
        "Upload a PDF",  # label above the box
        type=["pdf"],  # only allow .pdf files
    )  # the chosen file is saved in the variable uploaded_pdf (or None if nothing is chosen)

    if uploaded_pdf is not None:  # runs only after the user picks a file
        # st.session_state is Streamlit's memory that survives between reruns (every click reruns the script).
        # We only want to re-read and re-chunk the PDF when a NEW file is uploaded, not on every click,
        # so we remember the file's name and skip the work if it hasn't changed.
        if st.session_state.get("pdf_name") != uploaded_pdf.name:  # a new or different file was uploaded
            with st.spinner("Reading and splitting your PDF..."):  # shows a small loading spinner
                full_text = extract_text(uploaded_pdf)  # step A: read every page's text
                chunks = make_chunks(full_text)  # step B: cut that text into index cards
            st.session_state["pdf_name"] = uploaded_pdf.name  # remember which file we processed
            st.session_state["chunks"] = chunks  # store the cards for the chat section to use later
            st.session_state["chat_history"] = []  # start a fresh conversation for the new document

        size_kb = uploaded_pdf.size / 1024  # file size in bytes divided by 1024 gives kilobytes
        st.success(f"Received {uploaded_pdf.name} ({size_kb:.0f} KB)")  # green confirmation box
        st.info(f"Split into {len(st.session_state['chunks'])} chunks (index cards).")  # shows the card count

    st.caption("Works with text-based PDFs. Scanned pictures of pages need OCR, which we skip.")  # small grey note
    st.caption("Use a public document. Free AI services may use text you send to improve their models.")  # privacy note

# ---------- 5. Hero section (the big navy panel) ----------
# NOTE: the HTML below has no blank lines and no indentation on purpose.
# Streamlit's markdown treats indented text as code and blank lines as breaks.
HERO = """
<div class="hero">
<div>
<h1>Ask your document anything.</h1>
<p>Upload a PDF, ask in plain English, and see the exact passages behind every answer.</p>
<span class="chip">App is live. Chat arrives in the next step.</span>
</div>
<div class="stack">
<div class="card card-back"><small>Your question (sample)</small>How much is the late fee?</div>
<div class="card card-front"><small>Passage found in the PDF (sample)</small>Late returns cost 2 rupees per day, up to 100 rupees per book.</div>
</div>
</div>
"""  # end of hero HTML
st.markdown(HERO, unsafe_allow_html=True)  # draw the hero on the page

# ---------- 6. "How it works" section ----------
STEPS = """
<h2 class="how">How it works</h2>
<div class="steps">
<div class="step"><div class="num">1</div><h3>Upload</h3><p>Add a text-based PDF in the sidebar.</p></div>
<div class="step"><div class="num">2</div><h3>Split</h3><p>The app cuts it into short passages, like index cards.</p></div>
<div class="step"><div class="num">3</div><h3>Match</h3><p>Your question finds the passages closest in meaning.</p></div>
<div class="step"><div class="num">4</div><h3>Answer</h3><p>The AI replies using only those passages and shows them to you.</p></div>
</div>
"""  # end of steps HTML
st.markdown(STEPS, unsafe_allow_html=True)  # draw the four steps

# ---------- 7. Chat section ----------
st.markdown('<h2 class="how">Chat</h2>', unsafe_allow_html=True)  # reuse the "how" heading style for this title

if "chat_history" not in st.session_state:  # the very first time the page ever loads
    st.session_state["chat_history"] = []  # start with an empty conversation list

if "chunks" not in st.session_state:  # no PDF has been uploaded yet this session
    st.warning("Upload a PDF in the sidebar first, then ask a question below.")  # yellow reminder box
else:
    # --- replay the conversation so far ---
    for role, message in st.session_state["chat_history"]:  # each saved turn is a (role, text) pair
        with st.chat_message(role):  # draws a chat bubble styled for "user" or "assistant"
            st.write(message)  # puts the text inside that bubble

    # --- get a new question from the user ---
    question = st.chat_input("Ask something about your PDF...")  # the box at the bottom of the page
    if question:  # runs only once, right after the user presses Enter
        st.session_state["chat_history"].append(("user", question))  # save the user's turn
        with st.chat_message("user"):  # show their question immediately
            st.write(question)

        # PLACEholder reply for Step 1 only: real retrieval + Gemini answers arrive in Step 2.
        # For now we just show the single chunk that shares the most words with the question,
        # so you can see that chunking is actually working before we add real embeddings.
        question_words = set(question.lower().split())  # the question's words, lowercased, no duplicates
        best_chunk = max(  # pick the chunk that overlaps the question the most
            st.session_state["chunks"],
            key=lambda c: len(question_words & set(c.lower().split())),  # & = words shared by both
        )
        placeholder_answer = (
            "Step 1 placeholder — real AI answers come in Step 2.\n\n"
            f"Closest-matching chunk found by simple word overlap:\n\n> {best_chunk}"
        )
        st.session_state["chat_history"].append(("assistant", placeholder_answer))  # save the bot's turn
        with st.chat_message("assistant"):  # show the placeholder reply
            st.write(placeholder_answer)
