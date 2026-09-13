import json
import re
import sqlite3
import time
import urllib.parse
import urllib.request
import pandas as pd
import streamlit as st

# --- 0. Page Configuration & Custom Branding ---
st.set_page_config(
    page_title="StudyBuddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 1. Background Wallpaper Controller ---
st.sidebar.title("🎨 Customization")
bg_option = st.sidebar.selectbox(
    "Choose Background Style:",
    options=[
        "Default Dark",
        "Aesthetic Cozy Study",
        "Minimalist Nature",
        "Custom Image URL",
    ],
)

bg_css = ""
if bg_option == "Aesthetic Cozy Study":
  bg_url = "https://images.unsplash.com/photo-1516979187457-637abb4f9353?q=80&w=1920&auto=format&fit=crop"
  bg_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
elif bg_option == "Minimalist Nature":
  bg_url = "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?q=80&w=1920&auto=format&fit=crop"
  bg_css = f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
elif bg_option == "Custom Image URL":
  custom_url = st.sidebar.text_input(
      "Paste Image URL:",
      placeholder="https://example.com/image.jpg",
  )
  if custom_url.strip():
    bg_css = f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{custom_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """

if bg_css:
  st.markdown(bg_css, unsafe_allow_html=True)

# --- 2. Database Setup ---
conn = sqlite3.connect("study_tracker.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS study_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    hours REAL
)
""")

try:
  cursor.execute(
      "ALTER TABLE study_log ADD COLUMN date TEXT DEFAULT CURRENT_DATE"
  )
except sqlite3.OperationalError:
  pass

conn.commit()

# Session State Initializations
if "start_time" not in st.session_state:
  st.session_state.start_time = None
if "logged_hours" not in st.session_state:
  st.session_state.logged_hours = 0.0


# --- 3. Sidebar: In-App YouTube Search & Player ---
def search_youtube_video_id(query):
  """Fetches the top YouTube video ID for a given search query directly."""
  try:
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    req = urllib.request.Request(
        search_url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      html = response.read().decode("utf-8")
      video_ids = re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", html)
      if video_ids:
        return video_ids[0]
  except Exception:
    pass
  return None


st.sidebar.write("---")
st.sidebar.title("🎧 Focus Music Search")

song_query = st.sidebar.text_input(
    "Search any video or song:",
    placeholder="e.g., Lofi Hip Hop, Physics Wallah, Mozart",
)

video_id = None

if song_query.strip():
  with st.sidebar.spinner("Searching YouTube..."):
    video_id = search_youtube_video_id(song_query.strip())
    if video_id:
      st.sidebar.success(f"Playing: **{song_query}**")
    else:
      st.sidebar.warning("Could not find video. Playing default track.")
      video_id = "jfKfPfyJRdk"
else:
  st.sidebar.caption("Default Focus Track (Lofi Girl):")
  video_id = "jfKfPfyJRdk"

st.sidebar.video(f"https://www.youtube.com/watch?v={video_id}")
st.sidebar.write("---")

# --- 4. Sidebar: Stopwatch & Focus Timer ---
st.sidebar.subheader("⏱️ Study Stopwatch")
if st.sidebar.button("▶️ Start Stopwatch"):
  st.session_state.start_time = time.time()
  st.sidebar.success("Stopwatch started!")

if st.sidebar.button("⏹️ Stop & Record"):
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

st.sidebar.subheader("⏳ Live Focus Timer")
timer_duration = st.sidebar.selectbox(
    "Select Focus Duration:",
    options=[1, 5, 15, 25, 50],
    format_func=lambda x: f"{x} Minute{'s' if x > 1 else ''}",
)

# Fixed non-blocking Focus Timer
timer_display = st.sidebar.empty()
start_timer_btn = st.sidebar.button("Start Live Countdown")

if start_timer_btn:
  total_seconds = timer_duration * 60
  for remaining in range(total_seconds, -1, -1):
    mins, secs = divmod(remaining, 60)
    timer_display.markdown(f"### ⏳ `{mins:02d}:{secs:02d}`")
    time.sleep(1)
  timer_display.success(f"🎉 {timer_duration}-minute focus session completed!")

# --- 5. Main UI: Header & Study Logger ---
st.title("📚 StudyBuddy")
st.caption("Your all-in-one smart focus companion & productivity dashboard")

st.header("📝 Log a Study Session")
col1, col2 = st.columns(2)

with col1:
  subject = st.text_input(
      "What subject did you study?", placeholder="e.g., Python, Mathematics"
  )
with col2:
  hours = st.number_input(
      "How many hours?",
      min_value=0.0,
      step=0.01,
      value=st.session_state.logged_hours,
  )

if st.button("Save Session", use_container_width=True):
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

# --- 6. Main UI: AI Study Assistant ---
st.write("---")
st.header("🤖 Instant Study Assistant")
search_query = st.text_input(
    "Ask any study concept or definition:",
    placeholder="e.g., Python programming, Newton's 3rd law, SQL",
)

if st.button("Ask Assistant"):
  if search_query.strip():
    with st.spinner("Searching concept..."):
      try:
        query_text = search_query.strip()
        encoded_query = urllib.parse.quote(query_text)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

        req = urllib.request.Request(
            url, headers={"User-Agent": "StudyBuddy/1.0"}
        )
        with urllib.request.urlopen(req) as response:
          data = json.loads(response.read().decode())
          abstract = data.get("AbstractText", "")
          heading = data.get("Heading", query_text)

          if not abstract and data.get("RelatedTopics"):
            first_topic = data["RelatedTopics"][0]
            abstract = first_topic.get("Text", "")

          if abstract:
            st.success(f"**Answer for:** *{heading}*")
            st.write(abstract)
          else:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query_text.title())}"
            wiki_req = urllib.request.Request(
                wiki_url, headers={"User-Agent": "StudyBuddy/1.0"}
            )
            with urllib.request.urlopen(wiki_req) as wiki_resp:
              wiki_data = json.loads(wiki_resp.read().decode())
              wiki_extract = wiki_data.get("extract", "")
              if wiki_extract:
                st.success(f"**Answer for:** *{query_text.title()}*")
                st.write(wiki_extract)
              else:
                st.info(
                    f"💡 **Study Tip for '{query_text}':** Focus on main"
                    " definitions and practice core problem examples!"
                )
      except Exception:
        st.info(
            f"💡 **Study Tip for '{search_query}':** Focus on main definitions"
            " and practice core problem examples!"
        )
  else:
    st.warning("Please enter a question first.")

# --- 7. Main UI: History & Analytics ---
st.write("---")
st.header("📊 Your Study History & Analytics")

df = pd.read_sql_query(
    "SELECT id as 'ID', date as 'Date', subject as 'Subject', hours as 'Hours"
    " Studied' FROM study_log",
    conn,
)

if not df.empty:
  c1, c2 = st.columns([1, 1])

  with c1:
    st.subheader("Logged Records")
    st.dataframe(df, use_container_width=True)
    total_hours = round(df["Hours Studied"].sum(), 2)
    st.info(f"🏆 Total Hours Logged: **{total_hours} hrs**")

  with c2:
    st.subheader("Subject Breakdown")
    chart_data = df.groupby("Subject")["Hours Studied"].sum()
    st.bar_chart(chart_data)

  with st.expander("🗑️ Manage / Clear Data"):
    col_clear1, col_clear2 = st.columns(2)
    with col_clear1:
      if st.button("Clear All Logs"):
        cursor.execute("DELETE FROM study_log")
        cursor.execute("VACUUM")
        conn.commit()
        st.success("All logs cleared!")
        st.rerun()
    with col_clear2:
      delete_id = st.number_input("Enter ID to delete:", min_value=1, step=1)
      if st.button("Delete Specific Entry"):
        cursor.execute("DELETE FROM study_log WHERE id = ?", (delete_id,))
        conn.commit()
        st.success(f"Deleted Entry ID {delete_id}!")
        st.rerun()
else:
  st.write("No study sessions logged yet.")