import streamlit as st
import pyttsx3
from fpdf import FPDF
import random
import os
import time
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

# Custom CSS for Dark Fantasy Theme
st.markdown("""
<style>
    /* Dark Fantasy Background */
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #1A1F2E 100%);
        color: #E5E7EB;
        font-family: 'Arial', sans-serif;
    }

    /* Glowing Particles Effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(circle at 20% 80%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
                          radial-gradient(circle at 80% 20%, rgba(147, 51, 234, 0.1) 0%, transparent 50%),
                          radial-gradient(circle at 40% 40%, rgba(56, 189, 248, 0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* Neon Glow Headings */
    .neon-blue {
        color: #38BDF8;
        text-shadow: 0 0 10px #38BDF8, 0 0 20px #38BDF8, 0 0 30px #38BDF8;
        font-weight: bold;
    }

    .neon-purple {
        color: #9333EA;
        text-shadow: 0 0 10px #9333EA, 0 0 20px #9333EA, 0 0 30px #9333EA;
        font-weight: bold;
    }

    /* Glowing Pill Buttons */
    .glow-btn {
        background: linear-gradient(45deg, #38BDF8, #9333EA);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }

    .glow-btn:hover {
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.6), 0 0 35px rgba(147, 51, 234, 0.4);
        transform: translateY(-2px);
    }

    /* Main Header */
    .main-header {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #38BDF8, #9333EA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
    }

    /* Sidebar Styling */
    .sidebar-content {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* Story Display */
    .story-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }

    /* Typewriter Effect Placeholder */
    .typewriter {
        border-right: 2px solid #38BDF8;
        animation: blink 1s infinite;
    }

    @keyframes blink {
        0%, 50% { border-color: #38BDF8; }
        51%, 100% { border-color: transparent; }
    }

    /* Progress Animation */
    .typing-dots {
        display: inline-block;
    }

    .typing-dots::after {
        content: '...';
        animation: dots 1.5s infinite;
    }

    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }

    /* Floating Action Buttons */
    .fab {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(45deg, #38BDF8, #9333EA);
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);
        transition: all 0.3s ease;
    }

    .fab:hover {
        box-shadow: 0 6px 30px rgba(56, 189, 248, 0.5);
        transform: scale(1.1);
    }

    /* Icon Buttons */
    .icon-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.2rem;
        color: #E5E7EB;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .icon-btn:hover {
        background: rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }

    /* Circular Knob */
    .circular-knob {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: conic-gradient(#38BDF8 0deg, #38BDF8 var(--value), #1A1F2E var(--value), #1A1F2E 360deg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #E5E7EB;
        margin: 0 auto;
    }

    /* Chips */
    .chip {
        display: inline-block;
        background: rgba(56, 189, 248, 0.2);
        border: 1px solid #38BDF8;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        color: #38BDF8;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .chip:hover, .chip.selected {
        background: rgba(56, 189, 248, 0.4);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    /* Progress Bar */
    .custom-progress {
        width: 100%;
        height: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        overflow: hidden;
    }

    .custom-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #38BDF8, #9333EA);
        border-radius: 5px;
        transition: width 0.3s ease;
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

# Layout redesign: two-column layout with collapsible sidebar

# Sidebar container with collapsible panels
with st.sidebar.expander("🎛️ Story Controls", expanded=True):
    # Controls inside sidebar
    col1, col2 = st.columns(2)
    with col1:
        # Icon dropdown for Genre
        genre_options = {
            "Fantasy 🧝": "Fantasy",
            "Sci-Fi 🚀": "Sci-Fi",
            "Mystery 🕵️": "Mystery",
            "Romance ❤️": "Romance",
            "Horror 👻": "Horror",
            "Adventure 🗺️": "Adventure",
            "Comedy 😂": "Comedy",
            "Drama 🎭": "Drama"
        }
        genre_display = st.selectbox("Genre", list(genre_options.keys()), help="Choose the story genre")
        genre = genre_options[genre_display]
    with col2:
        # Icon dropdown for Tone
        tone_options = {
            "Dark 🌑": "Dark",
            "Whimsical 🦄": "Whimsical",
            "Poetic 🎼": "Poetic",
            "Satirical 🎭": "Satirical"
        }
        tone_display = st.selectbox("Tone", list(tone_options.keys()), help="Select the narrative tone")
        tone = tone_options[tone_display]

    # Circular knob for number of characters (simulate with slider and CSS)
    num_characters = st.slider("Number of Characters", 2, 5, 3, help="How many main characters?")
    # TODO: Add circular knob UI with live preview

    # Chips for twist style
    selected_twist = st.multiselect("Twist Style", TWIST_STYLES, default=[TWIST_STYLES[0]], help="Type of plot twist")
    twist_style = selected_twist[0] if selected_twist else TWIST_STYLES[0]

    # Progress bar + numeric input for story length
    story_length = st.number_input("Story Length (words)", min_value=500, max_value=2000, value=1000, step=100, help="Approximate word count")
    story_length_progress = st.progress((story_length - 500) / 1500)

    voice_style = st.selectbox("Voice Style", VOICE_STYLES, help="Narration voice style")

    surprise_me = st.button("🎲 Surprise Me!", help="Randomize all settings")
    if surprise_me:
        genre = random.choice(GENRES)
        twist_style = random.choice(TWIST_STYLES)
        num_characters = random.randint(2, 5)
        story_length = random.randint(500, 2000)
        tone = random.choice(TONES)
        st.success(f"✨ Randomized settings applied!")

    generate = st.button("🚀 Generate Story", help="Create a new story")
    if generate:
        # Typing dots animation in spinner
        spinner_placeholder = st.empty()
        progress_bar = st.progress(0)

        for i in range(100):
            dots = "." * ((i // 10) % 4)
            spinner_placeholder.markdown(f'<div class="typing-dots">🧠 AI is crafting your story{dots}</div>', unsafe_allow_html=True)
            progress_bar.progress(i + 1)
            time.sleep(0.05)  # Simulate processing time

        spinner_placeholder.empty()
        progress_bar.empty()

        raw_story = generate_story(genre, num_characters, twist_style, story_length, tone)

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

            # Enhanced confetti animation
            st.balloons()
            st.markdown("""
            <script>
                // Simple confetti effect
                for (let i = 0; i < 100; i++) {
                    const confetti = document.createElement('div');
                    confetti.style.position = 'fixed';
                    confetti.style.left = Math.random() * 100 + 'vw';
                    confetti.style.top = '-10px';
                    confetti.style.width = '10px';
                    confetti.style.height = '10px';
                    confetti.style.background = ['#38BDF8', '#9333EA', '#FFD700', '#FF6B6B'][Math.floor(Math.random() * 4)];
                    confetti.style.borderRadius = '50%';
                    confetti.style.zIndex = '9999';
                    confetti.style.animation = 'fall 3s linear forwards';
                    document.body.appendChild(confetti);
                    setTimeout(() => confetti.remove(), 3000);
                }
            </script>
            <style>
                @keyframes fall {
                    to { transform: translateY(100vh) rotate(360deg); }
                }
            </style>
            """, unsafe_allow_html=True)

# Display current story in scrollable card
if st.session_state.current_story:
    cs = st.session_state.current_story
    st.markdown("---")
    st.markdown(f'<h2 class="neon-blue">📚 Your {cs["genre"]} Story with a {cs["twist_style"]} Twist</h2>', unsafe_allow_html=True)

    # Scrollable story card
    st.markdown('<div class="story-card">', unsafe_allow_html=True)

    # Characters section with emoji header
    st.markdown('<h3 class="neon-purple">👥 Characters</h3>', unsafe_allow_html=True)
    if cs['characters']:
        for char in cs['characters']:
            st.markdown(f"• **{char}**")
    else:
        st.write("No characters generated.")

    st.markdown("---")

    # Setting section with emoji header
    st.markdown('<h3 class="neon-purple">🌍 Setting</h3>', unsafe_allow_html=True)
    st.write(cs['setting'] or "No setting generated.")

    st.markdown("---")

    # Story section with emoji header and typewriter effect simulation
    st.markdown('<h3 class="neon-purple">✨ The Story</h3>', unsafe_allow_html=True)
    if cs['story']:
        # Simulate typewriter effect by displaying text progressively
        story_placeholder = st.empty()
        story_text = cs['story']
        displayed_text = ""
        for char in story_text:
            displayed_text += char
            story_placeholder.markdown(f'<span class="typewriter">{displayed_text}</span>', unsafe_allow_html=True)
            time.sleep(0.01)  # Adjust speed as needed
        story_placeholder.markdown(story_text)  # Final display without animation
    else:
        st.write("No story generated.")

    st.markdown("---")

    # Twist section with emoji header
    st.markdown('<h3 class="neon-purple">😱 The Twist</h3>', unsafe_allow_html=True)
    st.write(cs['twist'] or "No twist explanation generated.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons with modern styling (remove duplicate buttons)
    st.markdown('<h3 class="neon-blue">🎬 Actions</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Play button with waveform animation
        if st.button("▶️ Narrate Story", key="narrate", help="Listen to the story"):
            with st.spinner("Narrating..."):
                narrate_story(cs['story'], voice_style)
            st.success("🎤 Narration completed!")
    with col2:
        # Icon button for PDF export
        if st.button("📄 Export PDF", key="pdf", help="Download as PDF"):
            export_pdf(cs['characters'], cs['setting'], cs['story'], cs['twist'], "story.pdf")
            st.success("📥 PDF exported!")
            with open("story.pdf", "rb") as f:
                st.download_button("Download PDF", f, "story.pdf")
    with col3:
        # Icon button for audio export
        if st.button("🎵 Export Audio", key="audio", help="Download as MP3"):
            export_audio(cs['story'], voice_style, "story.mp3")
            st.success("📥 Audio exported!")
            with open("story.mp3", "rb") as f:
                st.download_button("Download MP3", f, "story.mp3")
    with col4:
        # Continue Story button
        if st.button("📝 Continue Story", key="continue_story", help="Continue the story with a new chapter"):
            with st.spinner("Continuing story..."):
                continue_prompt = f"Continue the following story with a new chapter of similar length, keeping the same characters, but updating the setting and twist if necessary. Output in the exact same format as the original story.\n\nOriginal story:\n\n{cs['raw']}\n\nContinued story:"
                client = OllamaClient(model=MODEL)
                new_full = client.generate(continue_prompt)
                if new_full.startswith("Error"):
                    st.error(new_full)
                else:
                    new_characters, new_setting, new_story, new_twist = parse_story(new_full)
                    cs['characters'] = new_characters
                    cs['setting'] = new_setting
                    cs['story'] = new_story
                    cs['twist'] = new_twist
                    cs['raw'] = new_full
                    st.success("✨ Story continued!")
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
