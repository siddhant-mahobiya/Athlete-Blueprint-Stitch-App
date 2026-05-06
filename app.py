import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta

st.set_page_config(page_title="Athlete Blueprint", layout="wide")

# -----------------------------
# Constants
# -----------------------------
WORKDAY_START = time(11, 0)
WORKDAY_END = time(20, 0)
SLEEP_TIME = time(1, 0)
DAILY_LOOP_RESET = time(5, 0)
WORKOUT_START = time(20, 45)
WORKOUT_END = time(21, 45)
WATER_GOAL_L = 4.0
WATER_GOAL_ML = int(WATER_GOAL_L * 1000)

YOUTUBE_LINKS = {
    "Barbell Rows": "https://www.youtube.com/results?search_query=barbell+rows+form",
    "Lat Pulldowns": "https://www.youtube.com/results?search_query=lat+pulldown+form",
    "Face Pulls": "https://www.youtube.com/results?search_query=face+pulls+form",
    "Barbell Curls": "https://www.youtube.com/results?search_query=barbell+curls+form",
    "Close-Grip Bench Press": "https://www.youtube.com/results?search_query=close+grip+bench+press+form",
    "Overhead Press": "https://www.youtube.com/results?search_query=overhead+press+form",
    "Hanging Leg Raises": "https://www.youtube.com/results?search_query=hanging+leg+raises+form",
    "Bench Press": "https://www.youtube.com/results?search_query=bench+press+form",
    "Incline Dumbbell Press": "https://www.youtube.com/results?search_query=incline+dumbbell+press+form",
    "Pull-ups": "https://www.youtube.com/results?search_query=pull+ups+form",
    "T-Bar Rows": "https://www.youtube.com/results?search_query=t+bar+row+form",
    "Squats": "https://www.youtube.com/results?search_query=barbell+squat+form",
    "Romanian Deadlifts": "https://www.youtube.com/results?search_query=romanian+deadlift+form",
    "Leg Press": "https://www.youtube.com/results?search_query=leg+press+form",
}

SPLIT = {
    "Monday": ["Barbell Rows", "Lat Pulldowns", "Face Pulls"],
    "Tuesday": ["Barbell Curls", "Close-Grip Bench Press"],
    "Wednesday": ["Overhead Press", "Hanging Leg Raises"],
    "Thursday": ["Bench Press", "Incline Dumbbell Press"],
    "Friday": ["Pull-ups", "T-Bar Rows"],
    "Saturday": ["Squats", "Romanian Deadlifts", "Leg Press"],
    "Sunday": [],
}

# -----------------------------
# Session State
# -----------------------------
if "weight_log" not in st.session_state:
    st.session_state.weight_log = pd.DataFrame(columns=["date", "weight_kg"])

if "step_log" not in st.session_state:
    st.session_state.step_log = pd.DataFrame(columns=["date", "steps"])

# -----------------------------
# Helpers
# -----------------------------
now = datetime.now()
current_time = now.time()

def loop_day(dt: datetime) -> datetime:
    if dt.time() < DAILY_LOOP_RESET:
        return dt - timedelta(days=1)
    return dt

loop_reference = loop_day(now)
loop_day_name = loop_reference.strftime("%A")

is_tuesday = loop_day_name == "Tuesday"
fasting_locked = is_tuesday and current_time < time(20, 0)

# -----------------------------
# Header
# -----------------------------
st.title("Athlete Blueprint")
st.caption(
    "Workday: 11:00 AM–8:00 PM • Sleep: 1:00 AM • Daily Loop resets at 5:00 AM"
)

if fasting_locked:
    st.warning("Tuesday Mode: Water & Electrolyte Only until 8:00 PM")
    st.info("Electrolyte Reminder: Keep hydration and electrolytes up today.")

if WORKOUT_START <= current_time <= WORKOUT_END:
    st.success("Workout Window Active (8:45 PM–9:45 PM)")

# -----------------------------
# Sidebar: Hydration + Steps
# -----------------------------
st.sidebar.title("Hydration Tank")
water_ml = st.sidebar.number_input(
    "Water Consumed (ml)", min_value=0, max_value=WATER_GOAL_ML, step=250, value=1000
)
hydration_pct = int((water_ml / WATER_GOAL_ML) * 100)
st.sidebar.progress(min(hydration_pct, 100))
st.sidebar.caption(f"{hydration_pct}% of {WATER_GOAL_L:.1f}L goal")

steps_today = st.sidebar.number_input("Steps Today", min_value=0, step=500, value=6000)
if st.sidebar.button("Save Steps"):
    st.session_state.step_log = pd.concat(
        [
            st.session_state.step_log,
            pd.DataFrame([{ "date": loop_reference.date(), "steps": steps_today }])
        ],
        ignore_index=True,
    )
    st.sidebar.success("Steps saved.")

# -----------------------------
# Tabs
# -----------------------------
tab_diet, tab_workout, tab_insights = st.tabs(["Diet", "Workout", "Insights"])

with tab_diet:
    st.header("Diet Tracker")

    if fasting_locked:
        st.error("Water & Electrolyte Only (Meal inputs locked)")
    else:
        st.subheader("Breakfast")
        breakfast = st.selectbox(
            "Choose Breakfast",
            ["Idli", "Dosa", "Poha", "Boiled Eggs"],
        )
        st.checkbox("+ Whey Protein (Breakfast)")

        st.subheader("Lunch")
        lunch = st.selectbox(
            "Choose Lunch",
            ["Chicken Roll", "Chicken Curry/Rice"],
        )
        st.checkbox("+ Whey Protein (Lunch)")

        st.subheader("Dinner")
        dinner = st.selectbox(
            "Choose Dinner",
            ["Rice", "Curry"],
        )
        st.checkbox("+ Whey Protein (Dinner)")

        st.button("Save Meal Log")

with tab_workout:
    st.header("Workout Split")
    st.write(f"Today: **{loop_day_name}**")

    today_workout = SPLIT.get(loop_day_name, [])
    if not today_workout:
        st.info("Rest Day")
    else:
        st.subheader("Routine")
        for exercise in today_workout:
            link = YOUTUBE_LINKS.get(exercise, "")
            if link:
                st.markdown(f"- {exercise} ([Form Guide]({link}))")
            else:
                st.markdown(f"- {exercise}")

    st.caption("Workout Window: 8:45 PM–9:45 PM")

with tab_insights:
    st.header("Insights & Analytics")

    st.subheader("Sunday Weigh-ins")
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=75.0, step=0.1)
    if st.button("Save Weight"):
        st.session_state.weight_log = pd.concat(
            [
                st.session_state.weight_log,
                pd.DataFrame([{ "date": loop_reference.date(), "weight_kg": weight }])
            ],
            ignore_index=True,
        )
        st.success("Weight saved.")

    if not st.session_state.weight_log.empty:
        fig_weight = px.line(
            st.session_state.weight_log,
            x="date",
            y="weight_kg",
            title="Weight Trend",
            markers=True,
        )
        st.plotly_chart(fig_weight, use_container_width=True)

    if not st.session_state.step_log.empty:
        fig_steps = px.line(
            st.session_state.step_log,
            x="date",
            y="steps",
            title="Step Count Trend",
            markers=True,
        )
        st.plotly_chart(fig_steps, use_container_width=True)
