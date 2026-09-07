import streamlit as st
import joblib
import re
import os
import time
from datetime import datetime

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Emotion Analyzer",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==================================================
# EMOTION MAPPING & THEME
# ==================================================

emotion_mapping = {
    0: "sadness",
    1: "anger",
    2: "love",
    3: "surprise",
    4: "fear",
    5: "joy"
}

emotion_icons = {
    "sadness": "😢",
    "anger": "😡",
    "love": "❤️",
    "surprise": "😲",
    "fear": "😨",
    "joy": "😊"
}

emotion_colors = {
    "sadness": "#5B8DEF",
    "anger": "#EF5B5B",
    "love": "#EF5BA1",
    "surprise": "#F5A623",
    "fear": "#8E5BEF",
    "joy": "#4CAF50"
}

emotion_quotes = {
    "sadness": "It's okay to feel down sometimes — this too shall pass.",
    "anger": "Take a breath. Anger is valid, but it doesn't have to drive.",
    "love": "That's a beautiful feeling to hold onto.",
    "surprise": "Life's full of the unexpected!",
    "fear": "Courage isn't the absence of fear, it's moving forward anyway.",
    "joy": "Savor this moment — joy is worth celebrating."
}

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1116 0%, #161925 100%);
    }
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7F5BEF, #EF5BA1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #A0A4B8;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }
    .result-card {
        border-radius: 18px;
        padding: 1.6rem;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }
    .result-emotion {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    .quote-box {
        font-style: italic;
        color: #D8DAE5;
        text-align: center;
        margin-top: 0.5rem;
        padding: 0.8rem;
        border-left: 3px solid rgba(255,255,255,0.25);
        background: rgba(255,255,255,0.04);
        border-radius: 8px;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.6rem 0;
        transition: transform 0.15s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    .footer-note {
        text-align: center;
        color: #6B6F82;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# LOAD MODEL
# ==================================================

@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "sentiment.pkl")
    vectorizer_path = os.path.join(base_dir, "vectorizer.pkl")
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer


try:
    model, vectorizer = load_model()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

# ==================================================
# TEXT CLEANING
# ==================================================

def clean_text(txt):
    txt = re.sub(r'<.*?>', '', txt)
    txt = re.sub(r'http\S+|www\S+', '', txt)
    txt = ''.join(i for i in txt if i.isascii())
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt

# ==================================================
# SESSION STATE — HISTORY
# ==================================================

if "history" not in st.session_state:
    st.session_state.history = []

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("### ⚙️ About")
    st.write(
        "This app uses a trained ML model (TF-IDF + classifier) "
        "to detect the emotion behind a piece of text."
    )
    st.markdown("**Detectable emotions:**")
    for emo, icon in emotion_icons.items():
        st.write(f"{icon} {emo.capitalize()}")

    st.divider()
    st.markdown("### 🕓 Recent History")
    if st.session_state.history:
        for entry in reversed(st.session_state.history[-5:]):
            st.write(
                f"{emotion_icons.get(entry['emotion'], '💬')} "
                f"**{entry['emotion'].capitalize()}** — "
                f"_{entry['text'][:40]}{'...' if len(entry['text']) > 40 else ''}_"
            )
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption("No analyses yet — try one out!")

# ==================================================
# HEADER
# ==================================================

st.markdown('<div class="main-title">💬 Emotion Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Type something and let AI read between the lines.</div>',
    unsafe_allow_html=True
)

if not model_loaded:
    st.error(f"⚠️ Could not load model files: {load_error}")
    st.stop()

st.divider()

# ==================================================
# EXAMPLE PROMPTS
# ==================================================

st.markdown("**✨ Try an example:**")
example_cols = st.columns(3)
examples = [
    "I can't believe you did this to me!",
    "I'm so proud of how far we've come together.",
    "This place is so peaceful, it makes me smile."
]

if "widget_counter" not in st.session_state:
    st.session_state.widget_counter = 0
if "stored_text" not in st.session_state:
    st.session_state.stored_text = ""

def set_text(value):
    st.session_state.stored_text = value
    st.session_state.widget_counter += 1  # forces a brand-new widget instance

for col, example in zip(example_cols, examples):
    if col.button(example[:22] + "...", use_container_width=True):
        set_text(example)
        st.rerun()

# ==================================================
# TEXT INPUT
# ==================================================

current_key = f"text_area_main_{st.session_state.widget_counter}"

text = st.text_area(
    "Enter your text:",
    value=st.session_state.stored_text,
    placeholder="Example: I really loved this movie!",
    height=150,
    key=current_key
)
st.session_state.stored_text = text  # keep in sync with manual typing

char_count = len(text)
st.caption(f"📝 {char_count} characters")

analyze_col, clear_col = st.columns([3, 1])
analyze_clicked = analyze_col.button("🔍 Analyze Emotion", use_container_width=True, type="primary")
if clear_col.button("✖️ Clear", use_container_width=True):
    set_text("")
    st.rerun()

# ==================================================
# ANALYSIS
# ==================================================

if analyze_clicked:

    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Analyzing emotion..."):
            time.sleep(0.4)  # small delay for perceived smoothness

            cleaned_text = clean_text(text)
            text_tfidf = vectorizer.transform([cleaned_text])
            prediction = int(model.predict(text_tfidf)[0])
            emotion = emotion_mapping[prediction]
            color = emotion_colors.get(emotion, "#7F5BEF")
            icon = emotion_icons.get(emotion, "💬")

        # Save to history
        st.session_state.history.append({
            "text": text,
            "emotion": emotion,
            "time": datetime.now().strftime("%H:%M:%S")
        })

        # ---- Result card ----
        st.markdown(
            f"""
            <div class="result-card" style="background: linear-gradient(135deg, {color}33, {color}11); border: 1px solid {color}55;">
                <div style="font-size:3rem;">{icon}</div>
                <div class="result-emotion" style="color:{color};">{emotion.capitalize()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if emotion in ("joy", "love", "surprise"):
            st.balloons()

        st.markdown(
            f'<div class="quote-box">💭 {emotion_quotes.get(emotion, "")}</div>',
            unsafe_allow_html=True
        )

        # ---- Confidence ----
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(text_tfidf)[0]
            confidence = max(probabilities) * 100

            st.write("")
            st.markdown(f"**Confidence: {confidence:.2f}%**")
            st.progress(int(confidence))

            st.markdown("#### 📊 Emotion Breakdown")
            classes = model.classes_

            # Sort by probability descending for a cleaner view
            results = sorted(
                zip(classes, probabilities),
                key=lambda x: x[1],
                reverse=True
            )

            for class_id, probability in results:
                class_id = int(class_id)
                emotion_name = emotion_mapping[class_id]
                pct = probability * 100
                bar_color = emotion_colors.get(emotion_name, "#7F5BEF")
                bar_icon = emotion_icons.get(emotion_name, "💬")

                st.markdown(
                    f"""
                    <div style="margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                            <span>{bar_icon} {emotion_name.capitalize()}</span>
                            <span>{pct:.2f}%</span>
                        </div>
                        <div style="background:rgba(255,255,255,0.08); border-radius:6px; height:10px; overflow:hidden;">
                            <div style="width:{pct}%; background:{bar_color}; height:100%; border-radius:6px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # ---- Word stats expander ----
        with st.expander("🔎 Text details"):
            words = cleaned_text.split()
            st.write(f"**Word count:** {len(words)}")
            st.write(f"**Character count (cleaned):** {len(cleaned_text)}")
            st.write(f"**Cleaned text preview:** _{cleaned_text[:200]}_")

        # ---- Download report ----
        report = (
            f"Emotion Analysis Report\n"
            f"------------------------\n"
            f"Text: {text}\n"
            f"Predicted Emotion: {emotion.capitalize()}\n"
            f"Confidence: {confidence:.2f}%\n" if hasattr(model, "predict_proba") else
            f"Emotion Analysis Report\n------------------------\nText: {text}\nPredicted Emotion: {emotion.capitalize()}\n"
        )
        st.download_button(
            "⬇️ Download Result",
            data=report,
            file_name="emotion_result.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==================================================
# FOOTER
# ==================================================

st.markdown(
    '<div class="footer-note">Built with Streamlit • Powered by a TF-IDF + ML pipeline</div>',
    unsafe_allow_html=True
)