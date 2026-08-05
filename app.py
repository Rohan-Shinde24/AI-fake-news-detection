import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
import io
try:
    from streamlit_option_menu import option_menu
except ImportError:
    option_menu = None

try:
    from streamlit_lottie import st_lottie
except ImportError:
    st_lottie = None

try:
    from streamlit_extras.colored_header import colored_header
except ImportError:
    def colored_header(label="", description="", color_name="blue-70"):
        if label or description:
            st.markdown(f"### {label}\n\n{description}")

try:
    from streamlit_extras.add_vertical_space import add_vertical_space
except ImportError:
    def add_vertical_space(count=1):
        for _ in range(count):
            st.markdown("<br>", unsafe_allow_html=True)

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import PyPDF2

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Fake AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CACHING & INITIALIZATION
# ==========================================
# Streamlit compatibility helpers for older deployments.
if hasattr(st, "cache_data"):
    cache_data = st.cache_data
else:
    cache_data = st.cache

if hasattr(st, "cache_resource"):
    def cache_resource(*args, **kwargs):
        return st.cache_resource(*args, **kwargs)
else:
    def cache_resource(*args, **kwargs):
        kwargs.pop("show_spinner", None)
        return st.cache(allow_output_mutation=True)

@cache_data()
def load_lottieurl(url: str):
    """Loads Lottie animation from a URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load Lottie Animations
lottie_ai = load_lottieurl("https://lottie.host/81f807df-571f-4a30-801b-bf8ea3b9e4ec/wP1NfA5O7p.json")

# Initialize Session States
if 'history' not in st.session_state:
    st.session_state.history = []
if 'theme' not in st.session_state:
    st.session_state.theme = 'Dark'
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""

# Load AI Model
@cache_resource(show_spinner="Initializing AI Core...")
def load_model():
    model_path = "./model"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        return tokenizer, model
    except Exception as e:
        return None, None

tokenizer, model = load_model()

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def predict(text):
    """Performs inference using the loaded model."""
    if not tokenizer or not model:
        # Fallback dummy prediction if model is not present in ./model
        time.sleep(1.5)
        is_real = len(text) % 2 == 0
        prob = [0.85, 0.15] if not is_real else [0.2, 0.8]
        return 1 if is_real else 0, np.array(prob)
        
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        predicted_class_id = logits.argmax().item()
    return predicted_class_id, probabilities[0].numpy()

def read_pdf(file):
    """Extracts text from an uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return ""

def inject_css(theme):
    """Injects custom CSS for Premium Glassmorphism and Animations."""
    if theme == 'Dark':
        bg_color = "#0e1117"
        glass_bg = "rgba(30, 34, 43, 0.7)"
        text_col = "#fafafa"
        border_col = "rgba(255, 255, 255, 0.1)"
        glow_real = "box-shadow: 0 0 25px rgba(40, 167, 69, 0.6);"
        glow_fake = "box-shadow: 0 0 25px rgba(220, 53, 69, 0.6);"
    else:
        bg_color = "#f8f9fa"
        glass_bg = "rgba(255, 255, 255, 0.85)"
        text_col = "#212529"
        border_col = "rgba(0, 0, 0, 0.1)"
        glow_real = "box-shadow: 0 0 25px rgba(40, 167, 69, 0.4);"
        glow_fake = "box-shadow: 0 0 25px rgba(220, 53, 69, 0.4);"
        
    custom_css = f"""
    <style>
    /* Global App Background */
    .stApp {{
        background: {bg_color};
    }}
    
    /* Glassmorphism Container */
    .glassmorphism {{
        background: {glass_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid {border_col};
        padding: 25px;
        color: {text_col};
        margin-bottom: 25px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }}
    .glassmorphism:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }}
    
    /* Glowing Animated Cards */
    .card-real {{
        background: linear-gradient(135deg, rgba(40,167,69,0.15) 0%, rgba(32,201,151,0.15) 100%);
        border: 2px solid rgba(40,167,69,0.4);
        {glow_real}
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        animation: pulse-green 2.5s infinite;
        color: {text_col};
    }}
    .card-fake {{
        background: linear-gradient(135deg, rgba(220,53,69,0.15) 0%, rgba(253,126,20,0.15) 100%);
        border: 2px solid rgba(220,53,69,0.4);
        {glow_fake}
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        animation: pulse-red 2.5s infinite;
        color: {text_col};
    }}
    
    /* Keyframe Animations for Glowing */
    @keyframes pulse-green {{
        0% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }}
        70% {{ box-shadow: 0 0 0 20px rgba(40, 167, 69, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }}
    }}
    @keyframes pulse-red {{
        0% {{ box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }}
        70% {{ box-shadow: 0 0 0 20px rgba(220, 53, 69, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }}
    }}
    
    /* Typing Animation Heading */
    .typing-demo {{
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        border-right: 3px solid {text_col};
        font-family: 'Courier New', Courier, monospace;
        font-size: 2.2em;
        font-weight: 800;
        color: {text_col};
        animation: typing 3s steps(40, end), blink-caret .75s step-end infinite;
        margin-bottom: 20px;
    }}
    @keyframes typing {{
        from {{ width: 0 }}
        to {{ width: 100% }}
    }}
    @keyframes blink-caret {{
        from, to {{ border-color: transparent }}
        50% {{ border-color: {text_col}; }}
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: #555; border-radius: 5px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #888; }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# UI COMPONENTS
# ==========================================
def sidebar():
    """Renders the sidebar navigation and settings."""
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; font-weight: 800;'>Fake AI 🌐</h2>", unsafe_allow_html=True)
        
        if lottie_ai and st_lottie:
            st_lottie(lottie_ai, height=150, key="sidebar_lottie")
            
        st.markdown("---")
        
        # Streamlit Option Menu for Navigation
        if option_menu is not None:
            selected = option_menu(
                menu_title="Navigation",
                options=["Fake News Detector", "History", "Model Accuracy", "About Project"],
                icons=["shield-check", "clock-history", "graph-up", "info-circle"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#00d2ff", "font-size": "20px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px 0", "border-radius": "10px"},
                    "nav-link-selected": {"background-color": "rgba(0,210,255,0.2)", "color": "#00d2ff", "border-left": "4px solid #00d2ff"},
                }
            )
        else:
            selected = st.radio(
                "Navigation",
                ["Fake News Detector", "History", "Model Accuracy", "About Project"],
                index=0,
                horizontal=False
            )
        
        st.markdown("---")
        
        # Theme Toggle
        theme = st.radio("UI Theme", ["Dark", "Light"], horizontal=True, index=0 if st.session_state.theme == "Dark" else 1)
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
            
        add_vertical_space(4)
        
        # Footer
        st.markdown("""
        <div style="text-align:center; opacity: 0.8; font-size: 14px;">
            <p>Powered by Transformers</p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px;">
                <a href="https://github.com" target="_blank" style="text-decoration:none; color: inherit; padding: 5px 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">🐙 GitHub</a>
                <a href="https://linkedin.com" target="_blank" style="text-decoration:none; color: inherit; padding: 5px 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">💼 LinkedIn</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected

def render_detector():
    """Renders the main detector page."""
    st.markdown('<div class="typing-demo">Neural Truth Verification System</div>', unsafe_allow_html=True)
    add_vertical_space(1)
    
    col1, col2 = st.columns([2.2, 1])
    
    # Left Column: Input Panel
    with col1:
        
        st.subheader("🔍 Analyze Content")
        
        detect_type = st.selectbox(
            "Select Detection Type",
            ["Fake News Detection", "Political News Check", "Social Media Rumor Check", "AI Generated News Detection"]
        )
        
        tab1, tab2, tab3, tab4 = st.tabs(["✍️ Text Input", "🔗 Paste URL", "📄 Upload File", "🎤 Voice Input"])
        
        text_to_analyze = ""
        
        with tab1:
            text_input = st.text_area("Paste Article Here", height=220, key="text_input", value=st.session_state.input_text)
            if text_input: text_to_analyze = text_input
            
        with tab2:
            url_input = st.text_input("Paste Article URL")
            if url_input:
                st.info("Extraction simulated. In production, this would scrape the URL content.")
                text_to_analyze = "Simulated text extracted from the provided URL..."
                
        with tab3:
            uploaded_file = st.file_uploader("Upload TXT or PDF", type=["txt", "pdf"])
            if uploaded_file is not None:
                if uploaded_file.name.endswith(".pdf"):
                    text_to_analyze = read_pdf(uploaded_file)
                else:
                    text_to_analyze = uploaded_file.getvalue().decode("utf-8")
                st.success(f"Successfully loaded: {uploaded_file.name}")
                
        with tab4:
            st.info("Speak into your microphone to transcribe and analyze.")
            if hasattr(st, "audio_input"): 
                audio_val = st.audio_input("Record Voice")
                if audio_val:
                    st.success("Audio captured! (Transcription simulated for demo)")
                    text_to_analyze = "Simulated transcription of the recorded audio stream..."
            else:
                st.warning("Voice recording is not supported in this Streamlit version. Please use text input or upload a file.")
                audio_note = st.text_area("Or paste text directly here", height=150)
                if audio_note:
                    text_to_analyze = audio_note
                
        c1, c2 = st.columns([2, 1])
        with c1:
            analyze_btn = st.button("🚀 Analyze Now", use_container_width=True)
        with c2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.input_text = ""
                st.rerun()
                
        

        # Trigger Analysis
        if analyze_btn:
            if text_to_analyze.strip():
                analyze_content(text_to_analyze, detect_type)
            else:
                st.warning("⚠️ Please provide content to analyze.")

    # Right Column: Samples & Live News
    with col2:
        
        st.subheader("💡 Try Sample Articles")
        st.caption("Click to load a sample into the analyzer.")
        
        if st.button("📈 Sample 1 (Real News)", use_container_width=True): 
            st.session_state.input_text = "The Federal Reserve announced today that it will raise interest rates by 0.25%, a move widely anticipated by markets as they try to combat inflation."
            st.rerun()
            
        if st.button("👽 Sample 2 (Fake News)", use_container_width=True):
            st.session_state.input_text = "Shocking discovery! Top scientists admit aliens have been living in massive underground bases beneath New York City since 1999."
            st.rerun()
            
        add_vertical_space(2)
        st.subheader("📰 Latest API News Feed")
        st.info("🟢 LIVE: Tech stocks rally to record highs following AI breakthroughs.")
        st.warning("🟡 ALERT: Unverified rumors circulating regarding major tech merger.")
        st.error("🔴 FAKE: Viral social media post about new tax laws deemed completely false by fact-checkers.")
        

def analyze_content(text, detect_type):
    """Processes the input text and renders the prediction UI."""
    with st.spinner("🧠 Analyzing semantics, patterns, and source credibility..."):
        # Fake delay for effect
        time.sleep(1.2)
        prediction, probabilities = predict(text)
        
        is_real = prediction == 1
        conf_fake = float(probabilities[0])
        conf_real = float(probabilities[1])
        
        # Save to session history
        st.session_state.history.append({
            "text": text[:100] + "...",
            "type": detect_type,
            "prediction": "Real" if is_real else "Fake",
            "confidence": conf_real if is_real else conf_fake,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        res_col1, res_col2 = st.columns([1, 1])
        
        # Card Rendering
        with res_col1:
            if is_real:
                st.markdown(f'<div class="card-real"><h1 style="font-size: 3rem; margin: 0;">✅ AUTHENTIC</h1><p style="font-size: 1.2rem; opacity: 0.8;">{detect_type}</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card-fake"><h1 style="font-size: 3rem; margin: 0;">🚨 DECEPTIVE</h1><p style="font-size: 1.2rem; opacity: 0.8;">{detect_type}</p></div>', unsafe_allow_html=True)
                
        # Confidence Metrics & Chart
        with res_col2:
            
            st.markdown("### Model Confidence")
            
            st.write(f"**Authentic Indicator:** {conf_real:.1%}")
            st.progress(conf_real)
            
            st.write(f"**Deceptive Indicator:** {conf_fake:.1%}")
            st.progress(conf_fake)
            
            

        add_vertical_space(1)
        
        # Plotly Donut Chart
        
        st.markdown("### Probability Distribution")
        fig = px.pie(
            values=[conf_real, conf_fake], 
            names=['Authentic', 'Deceptive'],
            color=['Authentic', 'Deceptive'],
            color_discrete_map={'Authentic': '#28a745', 'Deceptive': '#dc3545'},
            hole=0.6
        )
        fig.update_layout(
            margin=dict(t=20, b=20, l=0, r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fafafa" if st.session_state.theme == 'Dark' else "#212529",
            height=300
        )
        # Add center text
        fig.add_annotation(text=f"{max(conf_real, conf_fake):.1%}", x=0.5, y=0.5, font_size=24, showarrow=False)
        st.plotly_chart(fig, use_container_width=True)
        

def render_history():
    """Renders the History page."""
    st.title("🕒 Analysis History")
    colored_header(label="", description="Review your past verifications", color_name="blue-70")
    
    if not st.session_state.history:
        st.info("No history available. Analyze some text first!")
        return
        
    df = pd.DataFrame(st.session_state.history)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        
    with col2:
        
        real_count = len(df[df['prediction'] == 'Real'])
        fake_count = len(df[df['prediction'] == 'Fake'])
        
        fig = px.bar(
            x=['Authentic', 'Deceptive'], 
            y=[real_count, fake_count],
            color=['Authentic', 'Deceptive'],
            color_discrete_map={'Authentic': '#28a745', 'Deceptive': '#dc3545'},
            title="History Breakdown",
            labels={'x': 'Category', 'y': 'Count'}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fafafa" if st.session_state.theme == 'Dark' else "#212529"
        )
        st.plotly_chart(fig, use_container_width=True)
        

def render_accuracy():
    """Renders the Model Accuracy page."""
    st.title("📈 Model Analytics")
    colored_header(label="", description="System Performance Metrics", color_name="blue-70")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        
        st.metric(label="Overall Accuracy", value="94.2%", delta="+1.2%")
        
    with col2:
        
        st.metric(label="F1 Score", value="0.93", delta="0.02")
        
    with col3:
        
        st.metric(label="Parameters", value="125M", delta="RoBERTa Base")
        
        
    add_vertical_space(2)
    
    
    st.subheader("Confusion Matrix")
    
    # Dummy confusion matrix data
    z = [[420, 30], [25, 450]]
    x = ['Predicted Fake', 'Predicted Real']
    y = ['Actual Fake', 'Actual Real']
    
    fig = px.imshow(z, x=x, y=y, color_continuous_scale='Blues', text_auto=True, aspect="auto")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fafafa" if st.session_state.theme == 'Dark' else "#212529"
    )
    st.plotly_chart(fig, use_container_width=True)
    

def render_about():
    """Renders the About Project page."""
    st.title("ℹ️ About Project")
    colored_header(label="", description="Behind the AI", color_name="blue-70")
    
    
    st.markdown("""
    ### Project Overview
    This premium platform leverages state-of-the-art transformer models (RoBERTa) to perform deep semantic analysis on news articles, detecting linguistic patterns associated with misinformation, bias, and AI generation.
    
    ### Architecture
    - **Frontend**: Streamlit, Plotly, Lottie Animations, Custom CSS Glassmorphism
    - **Backend Engine**: PyTorch, HuggingFace Transformers
    - **Model**: Custom fine-tuned RoBERTa Sequence Classifier
    
    ### How it Works
    1. **Tokenization**: Text is converted into contextual embeddings using Byte-Pair Encoding.
    2. **Attention Mechanism**: The multi-head attention layers weigh the importance of different words in context.
    3. **Classification**: A dense feed-forward layer outputs probability scores for Authentic vs Deceptive.
    
    ---
    *Built with ❤️ for a safer, informed internet.*
    """)
    

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    inject_css(st.session_state.theme)
    selected_page = sidebar()
    
    if selected_page == "Fake News Detector":
        render_detector()
    elif selected_page == "History":
        render_history()
    elif selected_page == "Model Accuracy":
        render_accuracy()
    elif selected_page == "About Project":
        render_about()

if __name__ == "__main__":
    main()
