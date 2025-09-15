import streamlit as st
import pyttsx3
from fpdf import FPDF
import random
import os
from ollama_client import OllamaClient

# Constants
MODEL = "llama2"
GENRES = ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Adventure", "Comedy", "Drama"]
TWIST_STYLES = ["Betrayal", "Identity Reveal", "Time Loop", "Supernatural Element", "Redemption", "Tragedy", "Victory"]
VOICE_STYLES = ["Narrator", "Horror", "Child", "Epic"]
TONES = ["Dark", "Whimsical", "Poetic", "Satirical"]

# Prompt template
PROMPT_TEMPLATE = """
You are an imaginative author who crafts unforgettable stories.
Your task is to generate a story experience based on the following inputs:
- Genre: {genre}
- Characters: {num_characters} unique characters
- Twist Style: {twist_style}
- Story Length: about {story_length} words
- Tone: {tone}
Instructions:
- Characters: Create {num_characters} characters with distinct names, traits, backstories, and personal conflicts. Each character should have a secret or hidden agenda that can fuel the twist.
- World-building: Describe the setting with vivid sensory details. Add cultural, historical, or fantastical elements appropriate to {genre}.
- Plot Development: Build tension as the characters' goals clash. Include dialogue that reveals personality and foreshadows the twist.
- Plot Twist: Introduce a {twist_style} twist near the end that dramatically changes how the reader understands the story. Ensure the twist feels surprising but logical in hindsight.
- Style: Use rich, cinematic prose. Balance action, description, and dialogue. Keep it engaging and immersive.
Output Format (follow exactly):
Characters:
- Character 1 bio
- Character 2 bio
Setting:
Setting description paragraph
Story:
Story narrative with twist
Twist:
Twist explanation
"""

# Function to generate story
def generate_story(genre, num_characters, twist_style, story_length, tone):
    prompt = PROMPT_TEMPLATE.format(genre=genre, num_characters=num_characters, twist_style=twist_style, story_length=story_length, tone=tone)
    client = OllamaClient(model=MODEL)
    return client.generate(prompt)

# Function to parse story
def parse_story(text):
    lines = text.split('\n')
    characters = []
    setting = []
    story = []
    twist = []
    current_section = None
    for line in lines:
        stripped = line.strip()
        if stripped == 'Characters:':
            current_section = 'characters'
            continue
        elif stripped == 'Setting:':
            current_section = 'setting'
            continue
        elif stripped == 'Story:':
            current_section = 'story'
            continue
        elif stripped == 'Twist:':
            current_section = 'twist'
            continue
        if current_section == 'characters':
            if stripped.startswith('-'):
                characters.append(stripped[1:].strip())
            elif stripped and not stripped.startswith(('Setting:', 'Story:', 'Twist:')):
                characters.append(stripped)
        elif current_section == 'setting':
            if stripped and not stripped.startswith(('Story:', 'Twist:')):
                setting.append(stripped)
        elif current_section == 'story':
            if stripped and not stripped.startswith('Twist:'):
                story.append(stripped)
        elif current_section == 'twist':
            if stripped:
                twist.append(stripped)
    return characters, ' '.join(setting), ' '.join(story), ' '.join(twist)

# TTS function
def narrate_story(text, voice_style):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voice_style == "Narrator":
        if voices:
            engine.setProperty('voice', voices[0].id)
    elif voice_style == "Horror":
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
    elif voice_style == "Child":
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 200)
    elif voice_style == "Epic":
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 120)
    engine.say(text)
    engine.runAndWait()

# Export to PDF
def export_pdf(characters, setting, story, twist, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI Storyteller", ln=True, align='C')
    pdf.cell(200, 10, txt="Characters:", ln=True)
    for char in characters:
        pdf.multi_cell(0, 10, "- " + char)
    pdf.cell(200, 10, txt="Setting:", ln=True)
    pdf.multi_cell(0, 10, setting)
    pdf.cell(200, 10, txt="Story:", ln=True)
    pdf.multi_cell(0, 10, story)
    pdf.cell(200, 10, txt="The Twist Explained:", ln=True)
    pdf.multi_cell(0, 10, twist)
    pdf.output(filename)

# Export audio
def export_audio(text, voice_style, filename):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voice_style == "Narrator":
        if voices:
            engine.setProperty('voice', voices[0].id)
    elif voice_style == "Horror":
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
    elif voice_style == "Child":
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 200)
    elif voice_style == "Epic":
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 120)
    engine.save_to_file(text, filename)
    engine.runAndWait()

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .story-section {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .sidebar-header {
        font-size: 1.5rem;
        color: #2196F3;
        margin-bottom: 1rem;
    }
    .generate-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    .action-btn {
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main app
st.markdown('<h1 class="main-header">📖 AI Storyteller</h1>', unsafe_allow_html=True)
st.markdown("Create unique, AI-generated stories with custom parameters!")

if 'stories' not in st.session_state:
    st.session_state.stories = []
if 'current_story' not in st.session_state:
    st.session_state.current_story = None

# Sidebar
st.sidebar.markdown('<h2 class="sidebar-header">🎛️ Story Controls</h2>', unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    genre = st.selectbox("Genre", GENRES, help="Choose the story genre")
with col2:
    tone = st.selectbox("Tone", TONES, help="Select the narrative tone")

num_characters = st.sidebar.slider("Number of Characters", 2, 5, 3, help="How many main characters?")
twist_style = st.sidebar.selectbox("Twist Style", TWIST_STYLES, help="Type of plot twist")
story_length = st.sidebar.slider("Story Length (words)", 500, 2000, 1000, help="Approximate word count")
voice_style = st.sidebar.selectbox("Voice Style", VOICE_STYLES, help="Narration voice style")

surprise_me = st.sidebar.button("🎲 Surprise Me!", help="Randomize all settings")
if surprise_me:
    genre = random.choice(GENRES)
    twist_style = random.choice(TWIST_STYLES)
    num_characters = random.randint(2, 5)
    story_length = random.randint(500, 2000)
    tone = random.choice(TONES)
    st.sidebar.success(f"✨ Randomized settings applied!")

generate = st.sidebar.button("🚀 Generate Story", help="Create a new story")
if generate:
    with st.spinner("🧠 AI is crafting your story..."):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
        raw_story = generate_story(genre, num_characters, twist_style, story_length, tone)
        progress_bar.empty()
        if raw_story.startswith("Error"):
            st.error(f"❌ {raw_story}")
        else:
            characters, setting, story, twist = parse_story(raw_story)
            current_story = {
                'genre': genre,
                'twist_style': twist_style,
                'characters': characters,
                'setting': setting,
                'story': story,
                'twist': twist,
                'raw': raw_story
            }
            st.session_state.current_story = current_story
            st.session_state.stories.append(current_story)
            st.success("🎉 Story generated successfully!")
            st.balloons()

# Display current story
if st.session_state.current_story:
    cs = st.session_state.current_story
    st.markdown("---")
    st.markdown(f"## 📚 Your {cs['genre']} Story with a {cs['twist_style']} Twist")

    # Characters section
    with st.expander("👥 Characters", expanded=True):
        st.markdown('<div class="story-section">', unsafe_allow_html=True)
        if cs['characters']:
            for char in cs['characters']:
                st.markdown(f"• {char}")
        else:
            st.write("No characters generated.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Setting section
    with st.expander("🌍 Setting", expanded=True):
        st.markdown('<div class="story-section">', unsafe_allow_html=True)
        st.write(cs['setting'] or "No setting generated.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Story section
    with st.expander("📖 The Story", expanded=True):
        st.markdown('<div class="story-section">', unsafe_allow_html=True)
        st.write(cs['story'] or "No story generated.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Twist section
    with st.expander("🤯 The Twist", expanded=True):
        st.markdown('<div class="story-section">', unsafe_allow_html=True)
        st.write(cs['twist'] or "No twist explanation generated.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    st.markdown("### 🎬 Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔊 Narrate Story", help="Listen to the story"):
            with st.spinner("Narrating..."):
                narrate_story(cs['story'], voice_style)
            st.success("🎤 Narration completed!")
    with col2:
        if st.button("📄 Export PDF", help="Download as PDF"):
            export_pdf(cs['characters'], cs['setting'], cs['story'], cs['twist'], "story.pdf")
            st.success("📥 PDF exported!")
            with open("story.pdf", "rb") as f:
                st.download_button("Download PDF", f, "story.pdf")
    with col3:
        if st.button("🎵 Export Audio", help="Download as MP3"):
            export_audio(cs['story'], voice_style, "story.mp3")
            st.success("📥 Audio exported!")
            with open("story.mp3", "rb") as f:
                st.download_button("Download MP3", f, "story.mp3")

    # Continuation buttons
    st.markdown("### ➕ Extend Your Story")
    col4, col5 = st.columns(2)
    with col4:
        if st.button("📝 Continue Story", help="Add a new chapter"):
            with st.spinner("Continuing story..."):
                continue_prompt = f"Continue the following story with a new chapter of similar length:\n\n{cs['raw']}\n\nNew chapter:"
                client = OllamaClient(model=MODEL)
                new_chapter = client.generate(continue_prompt)
                if new_chapter.startswith("Error"):
                    st.error(new_chapter)
                else:
                    cs['story'] += "\n\n**New Chapter**\n\n" + new_chapter
                    st.success("✨ Story continued!")
                    st.experimental_rerun()
    with col5:
        if st.button("🔄 Add Another Twist", help="Introduce a new twist"):
            with st.spinner("Adding twist..."):
                twist_prompt = f"Add another twist to the following story:\n\n{cs['raw']}\n\nAdditional twist:"
                client = OllamaClient(model=MODEL)
                new_twist = client.generate(twist_prompt)
                if new_twist.startswith("Error"):
                    st.error(new_twist)
                else:
                    cs['story'] += "\n\n**Additional Twist**\n\n" + new_twist
                    st.success("🎭 Twist added!")
                    st.experimental_rerun()

# Gallery
st.sidebar.header("Story Gallery")
if st.session_state.stories:
    story_options = [f"Story {i+1}: {s['genre']} - {s['twist_style']}" for i, s in enumerate(st.session_state.stories)]
    selected = st.sidebar.selectbox("Select Story", story_options)
    if selected:
        idx = story_options.index(selected)
        s = st.session_state.stories[idx]
        st.sidebar.write(f"Genre: {s['genre']}, Twist: {s['twist_style']}")
        if st.sidebar.button("Load Story"):
            st.session_state.current_story = s
            st.experimental_rerun()
