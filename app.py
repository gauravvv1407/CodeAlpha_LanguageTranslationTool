"""LinguaBridge - CodeAlpha Language Translation Tool.

Start with: python -m streamlit run app.py
The MyMemory API performs the translation; this app handles the interface.
"""

import html
import json
import re
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st




API_URL = "https://api.mymemory.translated.net/get"
MAX_CHARACTERS = 120  
LANGUAGES = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta",
    "Telugu": "te", "Marathi": "mr", "Gujarati": "gu", "Urdu": "ur",
    "French": "fr", "Spanish": "es", "German": "de", "Arabic": "ar",
    "Japanese": "ja", "Korean": "ko", "Chinese (Simplified)": "zh-CN",
}
EXAMPLES = (
    ("Everyday greeting", "Hello! How are you today?", "English", "Hindi"),
    ("Travel question", "Where is the nearest train station?", "English", "French"),
    ("Study sentence", "I am learning artificial intelligence.", "English", "Spanish"),
)




class TranslationError(Exception):
    """An input or service problem that can be displayed to the user."""


def normalize_translation(text: str) -> str:
    """Decode HTML entities and double-escaped Unicode from provider entries."""
    text = html.unescape(text)
    return re.sub(
        r"(?:\\u[0-9a-fA-F]{4})+",
        lambda match: json.loads('"' + match.group(0) + '"'),
        text,
    ).strip()


def similarity(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def parse_response(payload: dict, original_text: str) -> str:
    """Validate the service result; never display an API error as a translation."""
    if not isinstance(payload, dict):
        raise TranslationError("The translation service returned an unreadable result.")
    if payload.get("quotaFinished") or str(payload.get("responseStatus")) == "429":
        raise TranslationError("The service's usage limit was reached. Please try again later.")
    if str(payload.get("responseStatus")) != "200":
        detail = payload.get("responseDetails")
        detail = detail[:200] if isinstance(detail, str) else ""
        raise TranslationError(detail or "The service could not translate this language pair.")
    data = payload.get("responseData")
    if not isinstance(data, dict):
        raise TranslationError("The service returned no translation. Please try again.")
    translated = data.get("translatedText")
    best_score = similarity(data.get("match"))

 
    matches = payload.get("matches", [])
    if isinstance(matches, list):
        for candidate in matches:
            if not isinstance(candidate, dict):
                continue
            segment = candidate.get("segment")
            output = candidate.get("translation")
            score = similarity(candidate.get("match"))
            if (isinstance(segment, str) and isinstance(output, str)
                    and segment.strip().casefold() == original_text.strip().casefold()
                    and output.strip() and score > best_score):
                translated, best_score = output, score

    if not isinstance(translated, str) or not translated.strip():
        raise TranslationError("The service returned an empty translation. Try another sentence.")
    translated = normalize_translation(translated)
    if not translated:
        raise TranslationError("The service returned an empty translation. Please try again.")
    return translated


def translate_text(text: str, source: str, target: str) -> str:
    """Send one short passage to MyMemory using a timed HTTPS GET request."""
    text = text.strip()
    if not text:
        raise TranslationError("Enter some text before translating.")
    if len(text) > MAX_CHARACTERS or len(text.encode("utf-8")) > 500:
        raise TranslationError(f"Use a short passage of up to {MAX_CHARACTERS} characters.")
    if source not in LANGUAGES or target not in LANGUAGES:
        raise TranslationError("Choose a language from the dropdown lists.")
    if source == target:
        return text
    query = urlencode({"q": text, "langpair": f"{LANGUAGES[source]}|{LANGUAGES[target]}", "mt": 1})
    request = Request(f"{API_URL}?{query}", headers={
        "User-Agent": "CodeAlphaLanguageTranslationTool/1.0",
        "Accept": "application/json",
    })
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 429:
            raise TranslationError("The service is busy or its usage limit was reached. Try later.") from error
        raise TranslationError(f"The service returned HTTP {error.code}. Please try again later.") from error
    except (URLError, TimeoutError) as error:
        raise TranslationError("Couldn't reach the translation service. Check your internet connection and retry.") from error
    except (json.JSONDecodeError, UnicodeError) as error:
        raise TranslationError("The service returned an unreadable response. Please try again.") from error
    return parse_response(payload, text)




def initialize_state() -> None:
    defaults = {"input_text": "", "source_language": "English",
                "target_language": "Hindi", "result": None, "history": [], "error": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_text() -> None:
    st.session_state.input_text = ""
    st.session_state.result = None
    st.session_state.error = None


def swap_languages() -> None:
    source = st.session_state.source_language
    st.session_state.source_language = st.session_state.target_language
    st.session_state.target_language = source
    st.session_state.result = None
    st.session_state.error = None


def load_example(text: str, source: str, target: str) -> None:
    st.session_state.input_text = text
    st.session_state.source_language = source
    st.session_state.target_language = target
    st.session_state.result = None
    st.session_state.error = None


def run_translation() -> None:
    st.session_state.error = None
    st.session_state.result = None
    text = st.session_state.input_text.strip()
    source, target = st.session_state.source_language, st.session_state.target_language
    try:
        with st.spinner("Translating your text..."):
            output = translate_text(text, source, target)
    except TranslationError as error:
        st.session_state.error = str(error)
        return
    result = {"text": text, "translation": output, "source": source, "target": target,
              "time": datetime.now().strftime("%H:%M")}
    st.session_state.result = result
    st.session_state.history = [result] + st.session_state.history[:4]




STYLES = """
<style>
.stApp { background: #f6f8fb; color: #1e2c42; --text-color: #1e2c42; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 1150px; padding-top: 2rem; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
[data-testid="stSidebar"] * { color: #1e2c42; }
[data-testid="stMain"] label, [data-testid="stMain"] [role="tab"] { color: #43546e; }
.hero { background: linear-gradient(120deg, #173b51, #156c70); border-radius: 22px;
        padding: 32px 36px; margin-bottom: 24px; color: white; }
.hero .eyebrow { font-size: 11px; color: #b8e7e1; letter-spacing: 2px; font-weight: 700; }
.hero h1 { color: white; font-size: clamp(28px, 4vw, 43px); letter-spacing: -1.2px;
           padding: 12px 0; margin: 0; line-height: 1.15; }
.hero p { color: #dcefee; font-size: 15px; line-height: 1.7; margin: 0; }
.brand { font-size: 23px; font-weight: 750; margin: 12px 0 3px; letter-spacing: -0.6px; }
.section-label { color: #65788e; font-size: 11px; letter-spacing: 1.5px;
                 font-weight: 700; margin-bottom: 12px; }
.output-empty { background: #ffffff; border: 1px dashed #cfdce5; border-radius: 14px;
                min-height: 210px; padding: 28px; color: #7a8ca0;
                display: flex; align-items: center; justify-content: center; text-align: center; }
.stTextArea textarea { background: white; color: #1e2c42; font-size: 17px; line-height: 1.65; }
[data-testid="stCode"] { border: 1px solid #dce6ec; border-radius: 14px; }
[data-testid="stCode"] pre { background: white !important; min-height: 210px; }
[data-testid="stCode"] code { color: #1e2c42 !important; font-size: 17px; line-height: 1.75; }
.stButton > button, .stDownloadButton > button {
    border-radius: 11px; border: 1px solid #d6e1eb; background: white; color: #264254;
}
.stButton > button[kind="primary"] { background: #156c70; border-color: #156c70; color: white; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: #156c70; }
[data-baseweb="select"] > div { background: white; color: #1e2c42; }
.footer { color: #76889c; font-size: 12px; text-align: center; padding: 18px 0; }
@media(max-width:640px) { .hero { padding: 24px; } }
</style>
"""


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="brand">🌐 LinguaBridge</div>', unsafe_allow_html=True)
        st.caption("Language Translation Tool")
        st.divider()
        st.markdown("**Try an example**")
        for index, (label, text, source, target) in enumerate(EXAMPLES):
            st.button(label, key=f"example_{index}", on_click=load_example,
                      args=(text, source, target), use_container_width=True)
        st.caption("Examples fill the input. Press Translate to send them.")
        st.divider()
        st.markdown("**Recent translations**")
        if not st.session_state.history:
            st.caption("Your last five translations appear here.")
        for result in st.session_state.history:
            with st.expander(f"{result['source']} → {result['target']} · {result['time']}"):
                st.write(result["text"])
                st.divider()
                st.write(result["translation"])
        st.divider()
        st.caption("Powered by the MyMemory translation API. Internet access is required; "
                   "the service may impose usage limits.")


def main() -> None:
    st.set_page_config(page_title="LinguaBridge | Language Translator", page_icon="🌐", layout="wide")
    initialize_state()
    st.markdown(STYLES, unsafe_allow_html=True)
    render_sidebar()
    st.markdown(
        '<section class="hero"><div class="eyebrow">WORDS WITHOUT BORDERS</div>'
        '<h1>A little closer, in any language.</h1>'
        '<p>Translate short messages for study, travel, and everyday conversations.</p>'
        '</section>', unsafe_allow_html=True,
    )
    left, middle, right = st.columns([4, 1, 4])
    with left:
        st.selectbox("From", list(LANGUAGES), key="source_language")
    with middle:
        st.write("")
        st.button("⇄", help="Swap the selected languages", key="swap",
                  on_click=swap_languages, use_container_width=True)
    with right:
        st.selectbox("To", list(LANGUAGES), key="target_language")

    source_column, result_column = st.columns(2, gap="large")
    with source_column:
        st.markdown('<div class="section-label">YOUR MESSAGE</div>', unsafe_allow_html=True)
        text = st.text_area("Text to translate", key="input_text", max_chars=MAX_CHARACTERS,
                            height=220, placeholder="Enter a short sentence...", label_visibility="collapsed")
        st.caption(f"{len(text)} / {MAX_CHARACTERS} characters")
        translate_column, clear_column = st.columns([2, 1])
        with translate_column:
            st.button("Translate", key="translate", type="primary", on_click=run_translation,
                      use_container_width=True)
        with clear_column:
            st.button("Clear", key="clear", on_click=clear_text, use_container_width=True)
        st.caption("Text is sent to MyMemory when you press Translate.")

    with result_column:
        st.markdown('<div class="section-label">TRANSLATION</div>', unsafe_allow_html=True)
        if st.session_state.error:
            st.error(st.session_state.error)
        result = st.session_state.result
        if result:
            st.caption(f"Last result: {result['source']} → {result['target']}")
            st.code(result["translation"], language=None, wrap_lines=True)
            st.caption("Use the copy icon in the translation box to copy the text.")
            st.download_button("Download translation", data=result["translation"].encode("utf-8"),
                               file_name=f"translation_{LANGUAGES[result['target']]}.txt",
                               mime="text/plain; charset=utf-8", use_container_width=True)
            snapshot = (result["text"], result["source"], result["target"])
            current = (text.strip(), st.session_state.source_language, st.session_state.target_language)
            if snapshot != current:
                st.info("Your input changed. Press Translate to update the result.")
            elif result["source"] == result["target"]:
                st.info("Both languages are the same. Your original text is shown unchanged.")
        else:
            st.markdown('<div class="output-empty">Your translation will appear here.<br>'
                        'Choose two languages and press Translate.</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("Translation quality depends on the online service. Review the result for accuracy.")
    st.markdown('<div class="footer">Created by Gaurav Kumar · CodeAlpha AI Internship</div>',
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
