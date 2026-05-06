import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, time, timedelta

st.set_page_config(page_title="Athlete Blueprint", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #002b36;
    }
    [data-testid="stSidebar"] * {
        color: #f8f8f2;
    }
    [data-testid="stProgress"] > div > div {
        background-color: #00ff00;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
PLACEHOLDER_IMAGE_URL = "https://placehold.co/640x360?text=Exercise+Guide"
WGER_API_BASE = "https://wger.de/api/v2"

WORKOUT_DETAILS = {
    "Monday": [
        {
            "name": "Barbell Rows (Overhand Grip)",
            "sets_reps": "4 sets x 8 reps",
            "description": "Hinge at hips to 45°. Pull bar to lower ribs.",
            "steps": [
                "Set feet hip-width and hinge with a flat back.",
                "Pull bar to lower ribs, elbows close to torso.",
                "Lower under control and keep core braced.",
            ],
            "link": "https://www.youtube.com/watch?v=9efgcAjQe7E",
        },
        {
            "name": "Lat Pulldowns (Wide)",
            "sets_reps": "3 sets x 12 reps",
            "description": "Pull with elbows; avoid excessive lean back.",
            "steps": [
                "Grip bar wide and sit tall with chest up.",
                "Drive elbows down toward ribs, squeeze lats.",
                "Return slowly to full stretch without shrugging.",
            ],
            "link": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
        },
        {
            "name": "Single-Arm DB Rows",
            "sets_reps": "3 sets x 10 reps per side",
            "description": "One hand on bench for support. Pull DB to hip pocket.",
            "steps": [
                "Brace one hand on bench; back flat and hips square.",
                "Row dumbbell to hip pocket, elbow tight to body.",
                "Lower with control and keep shoulders level.",
            ],
            "link": "https://www.youtube.com/results?search_query=single+arm+dumbbell+row+form",
        },
        {
            "name": "Face Pulls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull rope toward forehead; flare elbows out.",
            "steps": [
                "Set cable at upper chest height with rope attachment.",
                "Pull toward forehead, elbows high and wide.",
                "Pause, then return with control.",
            ],
            "link": "https://www.youtube.com/watch?v=eIq5CB9JfKE",
        },
        {
            "name": "Barbell Shrugs",
            "sets_reps": "3 sets x 12 reps",
            "description": "Straight arms; squeeze traps at the top.",
            "steps": [
                "Hold bar with straight arms and tall posture.",
                "Lift shoulders straight up without rolling.",
                "Pause at the top, then lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=barbell+shrug+form",
        },
        {
            "name": "Hyper-extensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Slow, controlled movement to strengthen the lower back.",
            "steps": [
                "Set pad at hips; maintain neutral spine.",
                "Lower torso under control without rounding.",
                "Extend to neutral and squeeze glutes.",
            ],
            "link": "https://www.youtube.com/results?search_query=back+extension+form",
        },
        {
            "name": "Dead Hangs",
            "sets_reps": "3 sets to failure",
            "description": "Hang from a pull-up bar to stretch lats and build grip.",
            "steps": [
                "Grip bar shoulder-width and relax shoulders.",
                "Let body hang long while keeping core lightly braced.",
                "Hold until grip fails, then step down safely.",
            ],
            "link": "https://www.youtube.com/results?search_query=dead+hang+form",
        },
    ],
    "Tuesday": [
        {
            "name": "Barbell Curls",
            "sets_reps": "4 sets x 10 reps",
            "description": "No swinging; keep elbows pinned to ribs.",
            "steps": [
                "Stand tall, elbows tight to ribs, wrists neutral.",
                "Curl bar up without shoulder swing.",
                "Lower slowly to full extension.",
            ],
            "link": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
        },
        {
            "name": "Close-Grip Bench Press",
            "sets_reps": "3 sets x 8 reps",
            "description": "Hands shoulder-width apart. Focus on tricep drive.",
            "steps": [
                "Set grip just inside shoulder width and brace.",
                "Lower bar to lower chest with elbows tucked.",
                "Press up, focusing on triceps.",
            ],
            "link": "https://www.youtube.com/results?search_query=close+grip+bench+press+form",
        },
        {
            "name": "Hammer Curls",
            "sets_reps": "3 sets x 12 reps",
            "description": "Neutral grip (palms facing each other).",
            "steps": [
                "Stand tall with neutral grip and elbows at sides.",
                "Curl up keeping wrists neutral.",
                "Lower under control.",
            ],
            "link": "https://www.youtube.com/results?search_query=hammer+curls+form",
        },
        {
            "name": "Cable Overhead Tricep Extension",
            "sets_reps": "3 sets x 12 reps",
            "description": "Use a rope. Extend fully above the head.",
            "steps": [
                "Face away from cable, elbows tucked near ears.",
                "Extend elbows fully without flaring.",
                "Return slowly with upper arms steady.",
            ],
            "link": "https://www.youtube.com/results?search_query=overhead+tricep+extension+rope+form",
        },
        {
            "name": "Preacher Curls",
            "sets_reps": "3 sets x 12 reps",
            "description": "Prevents momentum; isolates the bicep peak.",
            "steps": [
                "Place arms on pad with elbows fixed.",
                "Curl up without lifting elbows.",
                "Lower slowly to full stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=preacher+curl+form",
        },
        {
            "name": "Tricep Rope Pushdowns",
            "sets_reps": "3 sets x 15 reps",
            "description": "Flare the rope at the bottom for maximum contraction.",
            "steps": [
                "Stand tall, elbows pinned to sides.",
                "Press rope down and flare at bottom.",
                "Return to 90° elbow bend.",
            ],
            "link": "https://www.youtube.com/results?search_query=tricep+rope+pushdown+form",
        },
        {
            "name": "Wrist Curls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Use a light barbell or dumbbells to build forearms.",
            "steps": [
                "Rest forearms on thighs or bench with wrists hanging.",
                "Curl wrists upward through full range.",
                "Lower slowly for stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=wrist+curls+form",
        },
    ],
    "Wednesday": [
        {
            "name": "Overhead Press (OHP)",
            "sets_reps": "4 sets x 6 reps",
            "description": "Tight core; press bar in a straight line up.",
            "steps": [
                "Set hands just outside shoulders; brace core.",
                "Press bar overhead with head moving through.",
                "Lower under control to upper chest.",
            ],
            "link": "https://www.youtube.com/watch?v=2yjwViIWrbA",
        },
        {
            "name": "Dumbbell Lateral Raises",
            "sets_reps": "4 sets x 15 reps",
            "description": "Lead with elbows; slight bend in the arms.",
            "steps": [
                "Hold dumbbells at sides with soft elbows.",
                "Raise to shoulder height, leading with elbows.",
                "Lower slowly without swinging.",
            ],
            "link": "https://www.youtube.com/watch?v=PPrchakdYTo",
        },
        {
            "name": "Reverse Pec Deck",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull back until arms are in line with shoulders.",
            "steps": [
                "Set seat so hands align with shoulders.",
                "Open arms wide while squeezing rear delts.",
                "Return under control.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+pec+deck+form",
        },
        {
            "name": "Front Raises",
            "sets_reps": "3 sets x 12 reps",
            "description": "Control the weight; avoid momentum.",
            "steps": [
                "Hold dumbbells in front with soft elbows.",
                "Raise to shoulder height, palms down.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+front+raise+form",
        },
        {
            "name": "Dumbbell Shrugs",
            "sets_reps": "3 sets x 15 reps",
            "description": "Hold the squeeze for 1 second at the top.",
            "steps": [
                "Stand tall with dumbbells at sides.",
                "Lift shoulders straight up and pause.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+shrug+form",
        },
        {
            "name": "Hanging Leg Raises",
            "sets_reps": "3 sets x 15 reps",
            "description": "Don’t swing; lift legs with your core.",
            "steps": [
                "Hang with shoulders active and core braced.",
                "Lift legs by curling pelvis upward.",
                "Lower slowly without swinging.",
            ],
            "link": "https://www.youtube.com/results?search_query=hanging+leg+raise+form",
        },
        {
            "name": "Plank",
            "sets_reps": "3 sets x 1 min",
            "description": "Squeeze glutes and abs; keep back flat.",
            "steps": [
                "Elbows under shoulders; body in straight line.",
                "Squeeze glutes and brace abs.",
                "Hold without letting hips sag.",
            ],
            "link": "https://www.youtube.com/results?search_query=plank+form",
        },
    ],
    "Thursday": [
        {
            "name": "Flat Bench Press",
            "sets_reps": "4 sets x 8 reps",
            "description": "Drive feet into the floor and keep shoulder blades retracted.",
            "steps": [
                "Set feet, arch slightly, and retract shoulder blades.",
                "Lower bar to mid-chest with control.",
                "Press up while keeping wrists stacked.",
            ],
            "link": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
        },
        {
            "name": "Incline DB Press",
            "sets_reps": "3 sets x 10 reps",
            "description": "Press up and slightly in; control the eccentric.",
            "steps": [
                "Set bench to 30–45° and plant feet.",
                "Lower dumbbells to upper chest with control.",
                "Press up and slightly in.",
            ],
            "link": "https://www.youtube.com/results?search_query=incline+dumbbell+press+form",
        },
        {
            "name": "Chest Flys",
            "sets_reps": "3 sets x 12 reps",
            "description": "Keep a soft elbow bend and stretch the pecs.",
            "steps": [
                "Lie back with arms over chest, slight elbow bend.",
                "Lower arms wide until pec stretch.",
                "Bring arms back together.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+chest+fly+form",
        },
        {
            "name": "Dips",
            "sets_reps": "3 sets to failure",
            "description": "Lean forward to target the chest.",
            "steps": [
                "Lock out on parallel bars, chest slightly forward.",
                "Lower until shoulders are just below elbows.",
                "Press up to full lockout.",
            ],
            "link": "https://www.youtube.com/results?search_query=chest+dips+form",
        },
        {
            "name": "Pushups",
            "sets_reps": "3 sets x 20 reps",
            "description": "Maintain a rigid plank; chest touches first.",
            "steps": [
                "Hands under shoulders, body in straight line.",
                "Lower chest toward floor while elbows track back.",
                "Press up without sagging hips.",
            ],
            "link": "https://www.youtube.com/results?search_query=push+up+form",
        },
        {
            "name": "Machine Chest Press",
            "sets_reps": "3 sets x 12 reps",
            "description": "Control the tempo for a strong squeeze.",
            "steps": [
                "Set seat so handles align mid-chest.",
                "Press forward and squeeze chest.",
                "Return slowly to start.",
            ],
            "link": "https://www.youtube.com/results?search_query=machine+chest+press+form",
        },
        {
            "name": "Cable Cross-overs",
            "sets_reps": "3 sets x 15 reps",
            "description": "Bring hands together at chest height.",
            "steps": [
                "Set cables high with slight forward lean.",
                "Sweep hands together at chest height.",
                "Return to stretch with control.",
            ],
            "link": "https://www.youtube.com/results?search_query=cable+crossover+form",
        },
    ],
    "Friday": [
        {
            "name": "Pull-ups / Assisted Pull-ups",
            "sets_reps": "3 sets x max reps",
            "description": "Full hang at the bottom; drive elbows to ribs.",
            "steps": [
                "Grip bar shoulder-width and start from dead hang.",
                "Pull chest to bar by driving elbows down.",
                "Lower with control to full hang.",
            ],
            "link": "https://www.youtube.com/results?search_query=pull+ups+form",
        },
        {
            "name": "T-Bar Rows",
            "sets_reps": "3 sets x 10 reps",
            "description": "Chest up; pull handle toward lower ribs.",
            "steps": [
                "Hinge at hips with neutral spine and chest up.",
                "Row handle toward lower ribs.",
                "Lower slowly with lats engaged.",
            ],
            "link": "https://www.youtube.com/results?search_query=t+bar+row+form",
        },
        {
            "name": "Straight Arm Pulldowns",
            "sets_reps": "3 sets x 12 reps",
            "description": "Keep arms straight; squeeze lats at the bottom.",
            "steps": [
                "Stand tall with slight hinge and straight arms.",
                "Pull bar down to thighs using lats.",
                "Return to overhead stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=straight+arm+pulldown+form",
        },
        {
            "name": "Reverse Pec Deck",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull back until arms are in line with shoulders.",
            "steps": [
                "Adjust seat so hands align with shoulders.",
                "Open arms wide and squeeze rear delts.",
                "Return slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+pec+deck+form",
        },
        {
            "name": "Hyperextensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Slow, controlled hinge to hit lower back.",
            "steps": [
                "Set pad at hips; keep spine neutral.",
                "Lower torso without rounding.",
                "Extend to neutral and squeeze glutes.",
            ],
            "link": "https://www.youtube.com/results?search_query=back+extension+form",
        },
        {
            "name": "Single-Arm DB Rows",
            "sets_reps": "3 sets x 10 reps",
            "description": "Pull the DB to the hip pocket; avoid torso rotation.",
            "steps": [
                "Brace with one hand, square hips and shoulders.",
                "Row dumbbell to hip pocket.",
                "Lower under control.",
            ],
            "link": "https://www.youtube.com/results?search_query=single+arm+dumbbell+row+form",
        },
        {
            "name": "Reverse Flys",
            "sets_reps": "3 sets x 15 reps",
            "description": "Lead with elbows and squeeze rear delts.",
            "steps": [
                "Hinge at hips with flat back and soft elbows.",
                "Raise arms out to sides, leading with elbows.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+fly+form",
        },
        {
            "name": "Russian Twists",
            "sets_reps": "3 sets x 20 reps",
            "description": "Rotate through torso; keep core braced.",
            "steps": [
                "Sit tall, lean back slightly, brace core.",
                "Rotate shoulders side to side.",
                "Keep hips stable and move through torso.",
            ],
            "link": "https://www.youtube.com/results?search_query=russian+twists+form",
        },
    ],
    "Saturday": [
        {
            "name": "Barbell Squats",
            "sets_reps": "4 sets x 8 reps",
            "description": "Brace core; drive knees out; chest up.",
            "steps": [
                "Set bar on upper back and brace core.",
                "Sit hips down and back, knees tracking toes.",
                "Drive up through mid-foot.",
            ],
            "link": "https://www.youtube.com/watch?v=ultWZbUMBa8",
        },
        {
            "name": "Romanian Deadlifts (RDLs)",
            "sets_reps": "3 sets x 10 reps",
            "description": "Hinge at hips; keep lats tight.",
            "steps": [
                "Stand tall, soft knees, bar close to thighs.",
                "Hinge back until hamstring stretch.",
                "Drive hips forward to stand.",
            ],
            "link": "https://www.youtube.com/results?search_query=romanian+deadlift+form",
        },
        {
            "name": "Leg Press",
            "sets_reps": "3 sets x 12 reps",
            "description": "Feet shoulder-width; control the descent.",
            "steps": [
                "Set feet shoulder-width on platform.",
                "Lower sled until thighs are parallel.",
                "Press up without locking knees.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+press+form",
        },
        {
            "name": "Leg Extensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Squeeze quads hard at the top.",
            "steps": [
                "Align knees with machine pivot.",
                "Extend legs to full lockout.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+extension+form",
        },
        {
            "name": "Leg Curls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Control the eccentric for hamstrings.",
            "steps": [
                "Set pad just above ankles and brace core.",
                "Curl heels toward glutes.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+curl+form",
        },
        {
            "name": "Standing Calf Raises",
            "sets_reps": "4 sets x 15 reps",
            "description": "Pause at the top; full stretch at bottom.",
            "steps": [
                "Stand tall with balls of feet on edge.",
                "Rise up and pause at top.",
                "Lower to full stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=standing+calf+raise+form",
        },
        {
            "name": "Walking Lunges",
            "sets_reps": "3 sets x 20 steps",
            "description": "Long stride and upright torso.",
            "steps": [
                "Step forward into a long stride.",
                "Lower until back knee nearly touches floor.",
                "Drive through front foot to step forward.",
            ],
            "link": "https://www.youtube.com/results?search_query=walking+lunge+form",
        },
    ],
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


@st.cache_data(show_spinner=False)
def get_wger_image(exercise_name: str) -> str:
    try:
        response = requests.get(
            f"{WGER_API_BASE}/exercise/",
            params={"language": 2, "status": 2, "search": exercise_name},
            timeout=8,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return ""
        exercise_id = results[0]["id"]
        image_response = requests.get(
            f"{WGER_API_BASE}/exerciseimage/",
            params={"exercise": exercise_id, "is_main": True},
            timeout=8,
        )
        image_response.raise_for_status()
        image_results = image_response.json().get("results", [])
        if not image_results:
            return ""
        return image_results[0].get("image", "")
    except requests.RequestException:
        return ""


def get_youtube_thumbnail(link: str) -> str:
    if "watch?v=" in link:
        video_id = link.split("watch?v=")[-1].split("&")[0]
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return PLACEHOLDER_IMAGE_URL


def render_steps(steps: list[str]) -> None:
    if steps:
        st.markdown("\n".join([f"- {step}" for step in steps]))


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
        st.selectbox(
            "Choose Breakfast",
            ["Idli", "Dosa", "Poha", "Boiled Eggs"],
        )
        st.checkbox("+ Whey Protein (Breakfast)")

        st.subheader("Lunch")
        st.selectbox(
            "Choose Lunch",
            ["Chicken Roll", "Chicken Curry/Rice"],
        )
        st.checkbox("+ Whey Protein (Lunch)")

        st.subheader("Dinner")
        st.selectbox(
            "Choose Dinner",
            ["Rice", "Curry"],
        )
        st.checkbox("+ Whey Protein (Dinner)")

        st.button("Save Meal Log")

with tab_workout:
    st.header("Workout Split")
    st.write(f"Today: **{loop_day_name}**")

    today_workout = WORKOUT_DETAILS.get(loop_day_name, [])
    if not today_workout:
        st.info("Rest Day")
    else:
        st.subheader("Routine")
        for exercise in today_workout:
            st.markdown(f"**{exercise['name']}**")
            if exercise["sets_reps"]:
                st.caption(exercise["sets_reps"])
            if exercise["description"]:
                st.write(exercise["description"])
            render_steps(exercise.get("steps", []))
            if exercise["link"]:
                st.link_button("Watch Form", exercise["link"])
            wger_image = get_wger_image(exercise.get("name", ""))
            if wger_image:
                st.image(wger_image, use_column_width=True)
            else:
                st.image(get_youtube_thumbnail(exercise.get("link", "")), use_column_width=True)
            st.divider()

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
