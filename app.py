# ============================================================
# Ask My PDF  -  Step 0: the page shell (no AI yet)
# Analogy: today we build the SHOP FRONT. Next steps add the kitchen (the RAG part).
# ============================================================

import streamlit as st  # Streamlit = turns Python code into a web page, no HTML server needed
from rag_core import extract_text, make_chunks, build_search_index, find_best_chunks, ask_gemini, find_saved_key  # our engine room

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


# ---------- 4. Sidebar (left panel): where the user uploads their PDF ----------
with st.sidebar:  # everything indented under this line appears in the sidebar
    st.subheader("Your document")  # small heading
    uploaded_pdf = st.file_uploader(  # draws an upload box
        "Upload a PDF",  # label above the box
        type=["pdf"],  # only allow .pdf files
    )  # the chosen file is saved in the variable uploaded_pdf (or None if nothing is chosen)

    if st.button("Or try the sample document"):  # a button so visitors can test without having a PDF
        st.session_state["use_sample"] = True  # remember that they chose the sample

    pdf_file, pdf_name = None, None  # will hold whichever file we end up using, and its name
    if uploaded_pdf is not None:  # the visitor uploaded their own PDF, so that wins
        pdf_file, pdf_name = uploaded_pdf, uploaded_pdf.name
        st.session_state["use_sample"] = False  # forget the sample choice
    elif st.session_state.get("use_sample"):  # no upload, but they pressed the sample button
        pdf_file, pdf_name = "sample.pdf", "sample.pdf (demo)"  # sample.pdf sits next to app.py in the repo

    if pdf_file is not None:  # runs once we have a file, uploaded or sample
        # st.session_state is Streamlit's memory that survives between reruns (every click reruns the script).
        # We only want to re-read and re-chunk the PDF when a NEW file is uploaded, not on every click,
        # so we remember the file's name and skip the work if it hasn't changed.
        if st.session_state.get("pdf_name") != pdf_name:  # a new or different file was uploaded
            with st.spinner("Reading, splitting, and indexing your PDF..."):  # shows a small loading spinner
                full_text = extract_text(pdf_file)  # step A: read every page's text
                chunks = make_chunks(full_text)  # step B: cut that text into index cards
                vectorizer, chunk_vectors = build_search_index(chunks)  # step C: score every card's words, once
            st.session_state["pdf_name"] = pdf_name  # remember which file we processed
            st.session_state["chunks"] = chunks  # store the cards for the chat section to use later
            st.session_state["vectorizer"] = vectorizer  # store the word-scorer so questions are scored the same way
            st.session_state["chunk_vectors"] = chunk_vectors  # store every card's numbers
            st.session_state["chat_history"] = []  # start a fresh conversation for the new document

        st.success(f"Using: {pdf_name}")  # green confirmation box
        st.info(f"Split into {len(st.session_state['chunks'])} chunks (index cards).")  # shows the card count

    st.caption("Works with text-based PDFs. Scanned pictures of pages need OCR, which we skip.")  # small grey note
    st.caption("Use a public document. Free AI services may use text you send to improve their models.")  # privacy note

    st.divider()  # a thin horizontal line, to visually separate the two sidebar sections
    st.subheader("AI settings")  # second sidebar heading

    # Prefer a key saved in Streamlit's secrets (st.secrets) so visitors to your LIVE app don't need
    # their own key. Locally, or if no secret is set, fall back to a text box so you can still test.
    saved_key = find_saved_key()  # looks for the key in Streamlit secrets (see rag_core.py)

    if saved_key:
        api_key = saved_key  # use the key stored in Streamlit Cloud's secrets
        st.caption("Using the Gemini API key saved in this app's secrets.")
    else:
        api_key = st.text_input("Gemini API key", type="password")  # type="password" hides what's typed
        st.caption("No saved key found — paste your Gemini API key here for now.")

    top_k = st.slider(  # lets you choose how many cards are sent to Gemini per question
        "Passages sent to the AI", min_value=1, max_value=8, value=5,
        help="More passages = more chance the answer is included, but more text for the AI to read.",
    )

# ---------- 5. Hero section (the big navy panel) ----------
# NOTE: the HTML below has no blank lines and no indentation on purpose.
# Streamlit's markdown treats indented text as code and blank lines as breaks.
HERO = """
<div class="hero">
<div>
<h1>Ask your document anything.</h1>
<p>Upload a PDF, ask in plain English, and see the exact passages behind every answer.</p>
<span class="chip">App is live. Upload a PDF and start chatting.</span>
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

        with st.chat_message("assistant"):  # show the bot's reply in a bubble
            if not api_key:  # no Gemini key available (neither secret nor typed)
                answer = "Please add a Gemini API key in the sidebar first."
                st.write(answer)
            else:
                with st.spinner("Searching your PDF and asking Gemini..."):
                    top_chunks = find_best_chunks(  # step 1: find the best-matching cards
                        question,
                        st.session_state["chunks"],
                        st.session_state["vectorizer"],
                        st.session_state["chunk_vectors"],
                        top_k=top_k,  # how many cards, from the sidebar slider
                    )
                    try:
                        answer = ask_gemini(question, top_chunks, api_key)  # step 2: Gemini answers from those cards
                    except Exception as error:  # catches bad keys, network errors, hitting a free-tier limit, etc.
                        answer = f"Something went wrong calling Gemini: {error}"
                st.write(answer)  # show the AI's answer
                with st.expander("Sources — the cards Gemini was given"):  # collapsible "show your work" section
                    for i, chunk in enumerate(top_chunks, start=1):  # number each source card
                        st.markdown(f"**Card {i}**")
                        st.caption(chunk)
        st.session_state["chat_history"].append(("assistant", answer))  # save the bot's turn for history replay
