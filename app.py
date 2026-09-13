import json
import random
import sqlite3
import urllib.parse
import urllib.request
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- 0. Page Configuration ---
st.set_page_config(
    page_title="CommuniMate - English & Communication Coach",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 1. Database Setup ---
conn = sqlite3.connect("communication_tracker.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS practice_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT DEFAULT CURRENT_DATE,
    activity_type TEXT,
    notes TEXT,
    score INTEGER
)
""")
conn.commit()

# --- 2. Sidebar Setup & Navigation ---
st.sidebar.title("🗣️ CommuniMate")
st.sidebar.caption("Master English & Communication Skills")

menu = st.sidebar.radio(
    "Select Practice Module:",
    [
        "🎭 Real-World Scenarios",
        "📖 Vocabulary & Idiom Builder",
        "✍️ Grammar & Expression Refiner",
        "⏱️ Speech & Fluency Timer",
        "📊 Progress Tracker",
    ],
)

# --- 3. Module 1: Real-World Scenarios ---
if menu == "🎭 Real-World Scenarios":
  st.title("🎭 Communication Practice Scenarios")
  st.caption("Practice how you would respond in everyday professional & social situations.")

  scenarios = {
      "Job Interview": "Interviewer: 'Can you tell me about a time you made a mistake at work and how you handled it?'",
      "Salary Negotiation": "Manager: 'We are offering you the standard starting rate for this role.'",
      "Ordering at a Cafe": "Barista: 'Hi! What can I get started for you today?'",
      "Resolving a Conflict": "Teammate: 'I feel like your part of the project was submitted too late.'",
      "Making Small Talk": "Colleague: 'So, do you have any fun plans for the weekend?'",
  }

  selected_scenario = st.selectbox("Choose a Scenario:", list(scenarios.keys()))
  st.info(f"**Situation:** {scenarios[selected_scenario]}")

  user_response = st.text_area("Type your response (How would you answer confidently?):")

  if st.button("Submit & Log Practice"):
    if user_response.strip():
      cursor.execute(
          "INSERT INTO practice_log (activity_type, notes, score) VALUES"
          " (?, ?, ?)",
          (f"Scenario: {selected_scenario}", user_response, 85),
      )
      conn.commit()
      st.success("Great job practicing! Response logged successfully.")
      st.markdown("**💡 Pro-Tip for this scenario:** Keep your tone polite, direct, and structured (State your point -> Give context -> Conclude clearly).")
    else:
      st.warning("Please type a response before submitting.")

# --- 4. Module 2: Vocabulary & Dictionary Search ---
elif menu == "📖 Vocabulary & Idiom Builder":
  st.title("📖 Vocabulary & Idiom Builder")
  st.caption("Learn new words, definitions, and idioms to express yourself clearly.")

  # Random Word Generator
  vocab_list = [
      ("Articulate", "Expressing oneself clearly and effectively in speech."),
      ("Eloquent", "Fluent or persuasive in speaking or writing."),
      ("Empathy", "The ability to understand and share the feelings of another."),
      ("Concise", "Giving a lot of information clearly and in a few words."),
      ("Assertion", "A confident and forceful statement of fact or belief."),
  ]

  if st.button("🎲 Get a Random Word Challenge"):
    word, definition = random.choice(vocab_list)
    st.success(f"**Word:** {word}\n\n**Definition:** {definition}")

  st.write("---")
  st.subheader("🔍 Look Up Any Word Definition")
  search_word = st.text_input("Enter any English word:")

  if st.button("Search Meaning"):
    if search_word.strip():
      try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(search_word.strip())}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
          data = json.loads(resp.read().decode())
          meanings = data[0]["meanings"][0]["definitions"][0]["definition"]
          example = data[0]["meanings"][0]["definitions"][0].get("example", "N/A")

          st.write(f"**Meaning of {search_word}:** {meanings}")
          st.write(f"**Example:** *{example}*")
      except Exception:
        st.error("Word not found. Please check the spelling!")

# --- 5. Module 3: Grammar & Refiner ---
elif menu == "✍️ Grammar & Expression Refiner":
  st.title("✍️ Grammar & Phrase Refiner")
  st.caption("Transform casual English into professional, confident communication.")

  st.subheader("🔁 Professional Phrase Transformer")
  casual_phrase = st.selectbox(
      "How to say casual phrases professionally:",
      [
          "I don't know.",
          "That's a bad idea.",
          "I need this ASAP.",
          "Can you repeat that?",
          "Sorry for the delay.",
      ],
  )

  refinements = {
      "I don't know.": "Let me look into that and get back to you with an update.",
      "That's a bad idea.": "I have a few concerns regarding that approach. Could we consider an alternative?",
      "I need this ASAP.": "When you have a moment, could you please prioritize this item?",
      "Can you repeat that?": "Could you please clarify that last point for me?",
      "Sorry for the delay.": "Thank you for your patience while I worked on this.",
  }

  st.success(f"**Professional Alternative:** *\"{refinements[casual_phrase]}\"*")

# --- 6. Module 4: Speech & Fluency Timer ---
elif menu == "⏱️ Speech & Fluency Timer":
  st.title("⏱️ Impromptu Speech Timer (1-Minute Challenge)")
  st.caption("Pick a topic and speak out loud continuously for 60 seconds to build fluency!")

  topics = [
      "The importance of effective listening in leadership.",
      "How social media changes human interaction.",
      "Describe your dream travel destination and why.",
      "One skill everyone should learn in life.",
      "A book or movie that changed your perspective.",
  ]

  if st.button("🎯 Generate Speech Topic"):
    st.session_state.speech_topic = random.choice(topics)

  if "speech_topic" in st.session_state:
    st.info(f"**Your Topic:** {st.session_state.speech_topic}")

  # 60 Second Countdown Timer using JavaScript
  timer_code = """
  <div style="text-align: center; font-family: Arial; background: #111; color: #fff; padding: 20px; border-radius: 10px;">
      <h2 id="timer" style="font-size: 40px; color: #00FF66;">60</h2>
      <button onclick="startTimer()" style="padding: 10px 20px; font-size: 16px; font-weight: bold; background: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer;">▶️ Start 60s Speaking Challenge</button>
  </div>
  <script>
  function startTimer() {
      var sec = 60;
      var timer = setInterval(function(){
          document.getElementById('timer').innerHTML = sec;
          sec--;
          if (sec < 0) {
              clearInterval(timer);
              document.getElementById('timer').innerHTML = "🎉 Time's Up!";
          }
      }, 1000);
  }
  </script>
  """
  components.html(timer_code, height=160)

# --- 7. Module 5: Progress Tracker ---
elif menu == "📊 Progress Tracker":
  st.title("📊 Practice Log & Analytics")
  
  df = pd.read_sql_query("SELECT id as 'ID', date as 'Date', activity_type as 'Activity', notes as 'Response' FROM practice_log", conn)

  if not df.empty:
    st.dataframe(df, use_container_width=True)
    st.info(f"🏆 Total Practice Sessions Completed: **{len(df)}**")
  else:
    st.write("No practice sessions logged yet. Try out the Real-World Scenarios module!")