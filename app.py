# ============================================================
# Ask My PDF  -  Step 0: the page shell (no AI yet)
# Analogy: today we build the SHOP FRONT. Next steps add the kitchen (the RAG part).
# ============================================================

import streamlit as st  # Streamlit = turns Python code into a web page, no HTML server needed

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
    if uploaded_pdf is not None:  # runs only after the user picks a file
        size_kb = uploaded_pdf.size / 1024  # file size in bytes divided by 1024 gives kilobytes
        st.success(f"Received {uploaded_pdf.name} ({size_kb:.0f} KB)")  # green confirmation box
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
