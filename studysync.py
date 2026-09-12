import sqlite3
import time
import pandas as pd
import streamlit as st

# --- 1. Database Setup (Safe Migration Check) ---
conn = sqlite3.connect("study_tracker.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS study_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    hours REAL
)
""")

# Automatically add missing 'date' column if running on older database files
try:
  cursor.execute(
      "ALTER TABLE study_log ADD COLUMN date TEXT DEFAULT CURRENT_DATE"
  )
except sqlite3.OperationalError:
  pass

conn.commit()

# --- App Memory for Timer & Auto-Fill ---
if "start_time" not in st.session_state:
  st.session_state.start_time = None

if "logged_hours" not in st.session_state:
  st.session_state.logged_hours = 0.0

# --- 2. Sidebar: Background Music & Focus Mode ---
st.sidebar.title("🎧 Focus Mode")
st.sidebar.write("Background Study Audio Player:")

# Working online stream (or replace with local file if saved in folder)
st.sidebar.audio(
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    format="audio/mp3",
    loop=True,
)
st.sidebar.write("---")

# --- 3. Sidebar: Background Study Stopwatch ---
st.sidebar.subheader("⏱️ Study Stopwatch")
if st.sidebar.button("▶️ Start Studying"):
  st.session_state.start_time = time.time()
  st.sidebar.success("Stopwatch active!")

if st.sidebar.button("⏹️ Stop Studying"):
  if st.session_state.start_time is not None:
    elapsed_seconds = time.time() - st.session_state.start_time
    elapsed_minutes = round(elapsed_seconds / 60, 2)
    elapsed_hours = round(elapsed_seconds / 3600, 2)

    st.session_state.logged_hours = (
        elapsed_hours if elapsed_hours > 0.01 else 0.01
    )
    st.sidebar.info(
        f"Session ended: **{elapsed_minutes} mins** ({elapsed_hours} hrs)"
    )
    st.session_state.start_time = None
  else:
    st.sidebar.error("Start the stopwatch first!")

st.sidebar.write("---")

# --- 4. Sidebar: Customizable Live Focus Countdown ---
st.sidebar.subheader("⏳ Live Focus Timer")

# Preferable timer duration selector
timer_duration = st.sidebar.selectbox(
    "Select Focus Duration:",
    options=[1, 5, 15, 25, 50],
    format_func=lambda x: f"{x} Minute{'s' if x > 1 else ''}",
)

if st.sidebar.button("Start Live Countdown"):
  total_seconds = timer_duration * 60
  timer_container = st.sidebar.empty()

  # Safe countdown loop that updates UI gracefully
  for i in range(total_seconds, -1, -1):
    mins, secs = divmod(i, 60)
    timer_container.markdown(f"### ⏳ `{mins:02d}:{secs:02d}`")
    time.sleep(1)

  timer_container.empty()
  st.sidebar.success(f"🎉 {timer_duration}-minute focus session completed!")

# --- 5. Main App UI: Data Logging ---
st.title("📚 StudySync Tracker")

st.header("Log a New Session")
subject = st.text_input(
    "What subject did you study?", placeholder="e.g., Python, Mathematics"
)
hours = st.number_input(
    "How many hours?",
    min_value=0.0,
    step=0.01,
    value=st.session_state.logged_hours,
)

if st.button("Save Session"):
  if subject.strip() and hours > 0:
    cursor.execute(
        "INSERT INTO study_log (subject, hours) VALUES (?, ?)",
        (subject.strip(), hours),
    )
    conn.commit()
    st.success(f"Successfully logged {hours} hours for '{subject.strip()}'.")
    st.session_state.logged_hours = 0.0
    st.rerun()
  else:
    st.error("Please enter a subject name and valid study hours.")

# --- 6. Main App UI: Instant Study Assistant ---
import json
import urllib.parse
import urllib.request

st.header("🤖 Instant Study Assistant")
search_query = st.text_input(
    "Ask any study question:",
    placeholder="e.g., Python programming, Newton's third law",
)

if st.button("Ask Assistant"):
  if search_query.strip():
    with st.spinner("Searching..."):
      try:
        # Query DuckDuckGo Instant Answer API
        query_text = search_query.strip()
        encoded_query = urllib.parse.quote(query_text)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

        req = urllib.request.Request(
            url, headers={"User-Agent": "StudySyncTracker/1.0"}
        )

        with urllib.request.urlopen(req) as response:
          data = json.loads(response.read().decode())
          abstract = data.get("AbstractText", "")
          heading = data.get("Heading", query_text)

          # Fallback to topic summary if main abstract is empty
          if not abstract and data.get("RelatedTopics"):
            first_topic = data["RelatedTopics"][0]
            abstract = first_topic.get("Text", "")

          if abstract:
            st.success(f"**Answer for:** *{heading}*")
            st.write(abstract)
          else:
            # Fallback to Wikipedia programming/study search if DuckDuckGo summary is blank
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query_text.title())}"
            wiki_req = urllib.request.Request(
                wiki_url, headers={"User-Agent": "StudySyncTracker/1.0"}
            )
            with urllib.request.urlopen(wiki_req) as wiki_resp:
              wiki_data = json.loads(wiki_resp.read().decode())
              wiki_extract = wiki_data.get("extract", "")
              if wiki_extract:
                st.success(f"**Answer for:** *{query_text.title()}*")
                st.write(wiki_extract)
              else:
                st.info(
                    f"💡 **Study Tip for '{query_text}':** Focus on core"
                    " definitions and practice 2–3 solved problems!"
                )
      except Exception:
        st.info(
            f"💡 **Study Tip for '{search_query}':** Focus on core definitions"
            " and practice 2–3 solved problems!"
        )
  else:
    st.warning("Please enter a question first.")
# --- 7. Main App UI: History, Analytics & Clear Data ---
st.header("Your Study History")
df = pd.read_sql_query(
    "SELECT id as 'ID', date as 'Date', subject as 'Subject', hours as 'Hours"
    " Studied' FROM study_log",
    conn,
)

if not df.empty:
  st.dataframe(df, use_container_width=True)
  total_hours = round(df["Hours Studied"].sum(), 2)
  st.info(f"🏆 Total Hours Studied So Far: **{total_hours}**")

  st.subheader("📊 Subject Breakdown")
  chart_data = df.groupby("Subject")["Hours Studied"].sum()
  st.bar_chart(chart_data)

  with st.expander("🗑️ Manage / Clear Data"):
    col_clear1, col_clear2 = st.columns(2)

    with col_clear1:
      if st.button("Clear All Data"):
        cursor.execute("DELETE FROM study_log")
        cursor.execute("VACUUM")
        conn.commit()
        st.success("All logs cleared!")
        st.rerun()

    with col_clear2:
      delete_id = st.number_input(
          "Enter ID to delete single entry:", min_value=1, step=1
      )
      if st.button("Delete Entry"):
        cursor.execute("DELETE FROM study_log WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Deleted Entry ID {delete_id}!")
        st.rerun()
else:
  st.write("No study sessions logged yet.")