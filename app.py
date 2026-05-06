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
STRENGTH_MET = 6.0

WORKOUT_DETAILS = {
    "Monday": [
        {
            "name": "Barbell Rows (Overhand Grip)",
            "sets_reps": "4 sets x 8 reps",
            "description": "Hinge at hips to 45°. Pull bar to lower ribs.",
            "steps": [
                "Plant feet, hinge, and lock a flat back with a tight brace.",
                "Row bar to lower ribs, elbows close, squeeze lats hard.",
                "Lower under control while keeping torso fixed.",
            ],
            "link": "https://www.youtube.com/watch?v=9efgcAjQe7E",
        },
        {
            "name": "Lat Pulldowns (Wide)",
            "sets_reps": "3 sets x 12 reps",
            "description": "Pull with elbows; avoid excessive lean back.",
            "steps": [
                "Sit tall with chest proud and grip wide.",
                "Drive elbows down to ribs, bar to upper chest.",
                "Control back to full stretch without shrugging.",
            ],
            "link": "https://www.youtube.com/watch?v=CAwf7n6Luuc",
        },
        {
            "name": "Single-Arm DB Rows",
            "sets_reps": "3 sets x 10 reps per side",
            "description": "One hand on bench for support. Pull DB to hip pocket.",
            "steps": [
                "Brace on the bench, square hips and shoulders.",
                "Row to the hip pocket, pause and squeeze.",
                "Lower slowly, keep your back flat.",
            ],
            "link": "https://www.youtube.com/results?search_query=single+arm+dumbbell+row+form",
        },
        {
            "name": "Face Pulls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull rope toward forehead; flare elbows out.",
            "steps": [
                "Set rope at upper chest height and step back to tension.",
                "Pull to the forehead, elbows high, rotate out.",
                "Return slow with shoulders down.",
            ],
            "link": "https://www.youtube.com/watch?v=eIq5CB9JfKE",
        },
        {
            "name": "Barbell Shrugs",
            "sets_reps": "3 sets x 12 reps",
            "description": "Straight arms; squeeze traps at the top.",
            "steps": [
                "Stand tall with arms long and core tight.",
                "Shrug straight up, pause hard at the top.",
                "Lower slowly—no rolling.",
            ],
            "link": "https://www.youtube.com/results?search_query=barbell+shrug+form",
        },
        {
            "name": "Hyper-extensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Slow, controlled movement to strengthen the lower back.",
            "steps": [
                "Set pad at hips and lock a neutral spine.",
                "Hinge down under control without rounding.",
                "Drive up to neutral and squeeze glutes.",
            ],
            "link": "https://www.youtube.com/results?search_query=back+extension+form",
        },
        {
            "name": "Dead Hangs",
            "sets_reps": "3 sets to failure",
            "description": "Hang from a pull-up bar to stretch lats and build grip.",
            "steps": [
                "Grip the bar, let shoulders relax, ribs down.",
                "Hang long and breathe with a light core brace.",
                "Hold to your limit, step down safely.",
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
                "Stand tall, elbows pinned, wrists neutral.",
                "Curl up without shoulder swing.",
                "Lower slow to full extension.",
            ],
            "link": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
        },
        {
            "name": "Close-Grip Bench Press",
            "sets_reps": "3 sets x 8 reps",
            "description": "Hands shoulder-width apart. Focus on tricep drive.",
            "steps": [
                "Grip just inside shoulders, set arch and feet.",
                "Lower to lower chest with elbows tucked.",
                "Press up, drive through triceps.",
            ],
            "link": "https://www.youtube.com/results?search_query=close+grip+bench+press+form",
        },
        {
            "name": "Hammer Curls",
            "sets_reps": "3 sets x 12 reps",
            "description": "Neutral grip (palms facing each other).",
            "steps": [
                "Neutral grip, elbows fixed at sides.",
                "Curl up with shoulders quiet.",
                "Lower slowly.",
            ],
            "link": "https://www.youtube.com/results?search_query=hammer+curls+form",
        },
        {
            "name": "Cable Overhead Tricep Extension",
            "sets_reps": "3 sets x 12 reps",
            "description": "Use a rope. Extend fully above the head.",
            "steps": [
                "Face away, elbows by ears, core tight.",
                "Extend fully without flaring.",
                "Return slowly, upper arms still.",
            ],
            "link": "https://www.youtube.com/results?search_query=overhead+tricep+extension+rope+form",
        },
        {
            "name": "Preacher Curls",
            "sets_reps": "3 sets x 12 reps",
            "description": "Prevents momentum; isolates the bicep peak.",
            "steps": [
                "Set arms on pad, elbows fixed.",
                "Curl to peak and squeeze.",
                "Lower slow to stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=preacher+curl+form",
        },
        {
            "name": "Tricep Rope Pushdowns",
            "sets_reps": "3 sets x 15 reps",
            "description": "Flare the rope at the bottom for maximum contraction.",
            "steps": [
                "Elbows pinned, slight forward lean.",
                "Press down and flare the rope.",
                "Return to 90° under control.",
            ],
            "link": "https://www.youtube.com/results?search_query=tricep+rope+pushdown+form",
        },
        {
            "name": "Wrist Curls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Use a light barbell or dumbbells to build forearms.",
            "steps": [
                "Rest forearms, wrists free to move.",
                "Curl up and squeeze forearms.",
                "Lower slow to full stretch.",
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
                "Grip just outside shoulders, brace glutes/abs.",
                "Press straight up and move head through.",
                "Lower to upper chest under control.",
            ],
            "link": "https://www.youtube.com/watch?v=2yjwViIWrbA",
        },
        {
            "name": "Dumbbell Lateral Raises",
            "sets_reps": "4 sets x 15 reps",
            "description": "Lead with elbows; slight bend in the arms.",
            "steps": [
                "Soft elbows, shoulders down and back.",
                "Raise to shoulder height, lead with elbows.",
                "Lower slow, no swing.",
            ],
            "link": "https://www.youtube.com/watch?v=PPrchakdYTo",
        },
        {
            "name": "Reverse Pec Deck",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull back until arms are in line with shoulders.",
            "steps": [
                "Set seat so hands align with shoulders.",
                "Open wide and squeeze rear delts.",
                "Return slow with control.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+pec+deck+form",
        },
        {
            "name": "Front Raises",
            "sets_reps": "3 sets x 12 reps",
            "description": "Control the weight; avoid momentum.",
            "steps": [
                "Dumbbells in front, soft elbows.",
                "Lift to shoulder height with control.",
                "Lower slow.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+front+raise+form",
        },
        {
            "name": "Dumbbell Shrugs",
            "sets_reps": "3 sets x 15 reps",
            "description": "Hold the squeeze for 1 second at the top.",
            "steps": [
                "Stand tall, arms long, neck relaxed.",
                "Shrug straight up and pause.",
                "Lower slow.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+shrug+form",
        },
        {
            "name": "Hanging Leg Raises",
            "sets_reps": "3 sets x 15 reps",
            "description": "Don’t swing; lift legs with your core.",
            "steps": [
                "Active hang, shoulders packed down.",
                "Lift legs by curling pelvis.",
                "Lower slow, no swing.",
            ],
            "link": "https://www.youtube.com/results?search_query=hanging+leg+raise+form",
        },
        {
            "name": "Plank",
            "sets_reps": "3 sets x 1 min",
            "description": "Squeeze glutes and abs; keep back flat.",
            "steps": [
                "Elbows under shoulders, body straight.",
                "Brace abs/glutes and breathe low.",
                "Hold steady without hip sag.",
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
                "Set feet, slight arch, shoulder blades packed.",
                "Lower to mid-chest with wrists stacked.",
                "Press up and drive through the floor.",
            ],
            "link": "https://www.youtube.com/watch?v=rT7DgCr-3pg",
        },
        {
            "name": "Incline DB Press",
            "sets_reps": "3 sets x 10 reps",
            "description": "Press up and slightly in; control the eccentric.",
            "steps": [
                "Bench 30–45°, shoulder blades set.",
                "Lower to upper chest with control.",
                "Press up and slightly in.",
            ],
            "link": "https://www.youtube.com/results?search_query=incline+dumbbell+press+form",
        },
        {
            "name": "Chest Flys",
            "sets_reps": "3 sets x 12 reps",
            "description": "Keep a soft elbow bend and stretch the pecs.",
            "steps": [
                "Arms over chest, soft elbow bend.",
                "Open wide to feel a pec stretch.",
                "Bring back together and squeeze.",
            ],
            "link": "https://www.youtube.com/results?search_query=dumbbell+chest+fly+form",
        },
        {
            "name": "Dips",
            "sets_reps": "3 sets to failure",
            "description": "Lean forward to target the chest.",
            "steps": [
                "Lock out on bars, chest slightly forward.",
                "Lower until shoulders pass elbows.",
                "Press to full lockout.",
            ],
            "link": "https://www.youtube.com/results?search_query=chest+dips+form",
        },
        {
            "name": "Pushups",
            "sets_reps": "3 sets x 20 reps",
            "description": "Maintain a rigid plank; chest touches first.",
            "steps": [
                "Hands under shoulders, body plank.",
                "Lower chest with elbows ~45°.",
                "Press up, keep hips level.",
            ],
            "link": "https://www.youtube.com/results?search_query=push+up+form",
        },
        {
            "name": "Machine Chest Press",
            "sets_reps": "3 sets x 12 reps",
            "description": "Control the tempo for a strong squeeze.",
            "steps": [
                "Set seat so handles hit mid-chest.",
                "Press and squeeze the chest.",
                "Return slow with control.",
            ],
            "link": "https://www.youtube.com/results?search_query=machine+chest+press+form",
        },
        {
            "name": "Cable Cross-overs",
            "sets_reps": "3 sets x 15 reps",
            "description": "Bring hands together at chest height.",
            "steps": [
                "Set cables high with a slight forward lean.",
                "Sweep hands together at chest height.",
                "Return to stretch under control.",
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
                "Lower under control to full hang.",
            ],
            "link": "https://www.youtube.com/results?search_query=pull+ups+form",
        },
        {
            "name": "T-Bar Rows",
            "sets_reps": "3 sets x 10 reps",
            "description": "Chest up; pull handle toward lower ribs.",
            "steps": [
                "Hinge at hips, chest up, brace hard.",
                "Row handle to lower ribs.",
                "Lower slow with lats engaged.",
            ],
            "link": "https://www.youtube.com/results?search_query=t+bar+row+form",
        },
        {
            "name": "Straight Arm Pulldowns",
            "sets_reps": "3 sets x 12 reps",
            "description": "Keep arms straight; squeeze lats at the bottom.",
            "steps": [
                "Slight hinge, arms straight, lats tight.",
                "Pull bar to thighs with lats.",
                "Return slow to overhead stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=straight+arm+pulldown+form",
        },
        {
            "name": "Reverse Pec Deck",
            "sets_reps": "3 sets x 15 reps",
            "description": "Pull back until arms are in line with shoulders.",
            "steps": [
                "Set seat so hands align with shoulders.",
                "Open wide and squeeze rear delts.",
                "Return slow and controlled.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+pec+deck+form",
        },
        {
            "name": "Hyperextensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Slow, controlled hinge to hit lower back.",
            "steps": [
                "Pad at hips, spine neutral, core tight.",
                "Hinge down without rounding.",
                "Extend to neutral and squeeze glutes.",
            ],
            "link": "https://www.youtube.com/results?search_query=back+extension+form",
        },
        {
            "name": "Single-Arm DB Rows",
            "sets_reps": "3 sets x 10 reps",
            "description": "Pull the DB to the hip pocket; avoid torso rotation.",
            "steps": [
                "Brace with one hand, hips and shoulders square.",
                "Row to hip pocket and pause.",
                "Lower under control.",
            ],
            "link": "https://www.youtube.com/results?search_query=single+arm+dumbbell+row+form",
        },
        {
            "name": "Reverse Flys",
            "sets_reps": "3 sets x 15 reps",
            "description": "Lead with elbows and squeeze rear delts.",
            "steps": [
                "Hinge at hips, soft elbows, neck long.",
                "Raise arms out, lead with elbows.",
                "Lower slow with control.",
            ],
            "link": "https://www.youtube.com/results?search_query=reverse+fly+form",
        },
        {
            "name": "Russian Twists",
            "sets_reps": "3 sets x 20 reps",
            "description": "Rotate through torso; keep core braced.",
            "steps": [
                "Lean back slightly, chest up, core tight.",
                "Rotate shoulders side to side.",
                "Keep hips still and move through torso.",
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
                "Set bar, brace hard, feet shoulder-width.",
                "Sit down and back, knees track toes.",
                "Drive up through mid-foot.",
            ],
            "link": "https://www.youtube.com/watch?v=ultWZbUMBa8",
        },
        {
            "name": "Romanian Deadlifts (RDLs)",
            "sets_reps": "3 sets x 10 reps",
            "description": "Hinge at hips; keep lats tight.",
            "steps": [
                "Soft knees, bar close, lats tight.",
                "Hinge back to hamstring stretch.",
                "Drive hips forward to stand.",
            ],
            "link": "https://www.youtube.com/results?search_query=romanian+deadlift+form",
        },
        {
            "name": "Leg Press",
            "sets_reps": "3 sets x 12 reps",
            "description": "Feet shoulder-width; control the descent.",
            "steps": [
                "Feet shoulder-width, knees in line.",
                "Lower to parallel under control.",
                "Press up without locking knees.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+press+form",
        },
        {
            "name": "Leg Extensions",
            "sets_reps": "3 sets x 15 reps",
            "description": "Squeeze quads hard at the top.",
            "steps": [
                "Align knee with machine pivot.",
                "Extend and squeeze quads.",
                "Lower slow.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+extension+form",
        },
        {
            "name": "Leg Curls",
            "sets_reps": "3 sets x 15 reps",
            "description": "Control the eccentric for hamstrings.",
            "steps": [
                "Pad above ankles, hips down.",
                "Curl heels to glutes.",
                "Lower slow.",
            ],
            "link": "https://www.youtube.com/results?search_query=leg+curl+form",
        },
        {
            "name": "Standing Calf Raises",
            "sets_reps": "4 sets x 15 reps",
            "description": "Pause at the top; full stretch at bottom.",
            "steps": [
                "Balls of feet on edge, stand tall.",
                "Rise up and pause at the top.",
                "Lower to a full stretch.",
            ],
            "link": "https://www.youtube.com/results?search_query=standing+calf+raise+form",
        },
        {
            "name": "Walking Lunges",
            "sets_reps": "3 sets x 20 steps",
            "description": "Long stride and upright torso.",
            "steps": [
                "Take a long step, chest up.",
                "Drop back knee under hip.",
                "Drive through front foot to step forward.",
            ],
            "link": "https://www.youtube.com/results?search_query=walking+lunge+form",
        },
    ],
    "Sunday": [],
}

BREAKFAST_ITEMS = {
    "Idli": 160,
    "Puri": 210,
    "Dosa": 190,
    "Bread": 140,
    "Butter": 100,
    "Other": 0,
}
LUNCH_ITEMS = {
    "Rice + Curry": 450,
    "Biryani": 550,
    "Rolls": 420,
    "Chappati": 280,
    "Other": 0,
}
DINNER_ITEMS = {
    "Eggs": 140,
    "Curry": 220,
    "Rice": 200,
    "Dal": 190,
    "Other": 0,
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


def parse_sets_reps(sets_reps: str) -> tuple[int, int]:
    if not sets_reps:
        return 0, 0
    tokens = sets_reps.lower().replace("x", " ").replace("sets", " ").replace("reps", " ")
    parts = [int("".join(filter(str.isdigit, part))) for part in tokens.split() if any(ch.isdigit() for ch in part)]
    if len(parts) >= 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], 0
    return 0, 0


def calories_burned(weight_kg: float, minutes: float, met: float = STRENGTH_MET) -> float:
    return met * weight_kg * minutes * 3.5 / 200


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
        total_calories = 0

        st.subheader("Breakfast")
        for item, calories in BREAKFAST_ITEMS.items():
            if st.checkbox(f"{item} ({calories} kcal)", key=f"breakfast_{item}"):
                if item == "Other":
                    custom_food = st.text_input("Breakfast item", key="breakfast_custom")
                    custom_cal = st.number_input("Breakfast calories", min_value=0, step=10, key="breakfast_custom_cal")
                    if custom_food:
                        total_calories += custom_cal
                else:
                    total_calories += calories

        st.subheader("Lunch")
        for item, calories in LUNCH_ITEMS.items():
            if st.checkbox(f"{item} ({calories} kcal)", key=f"lunch_{item}"):
                if item == "Other":
                    custom_food = st.text_input("Lunch item", key="lunch_custom")
                    custom_cal = st.number_input("Lunch calories", min_value=0, step=10, key="lunch_custom_cal")
                    if custom_food:
                        total_calories += custom_cal
                else:
                    total_calories += calories

        st.subheader("Dinner")
        for item, calories in DINNER_ITEMS.items():
            if st.checkbox(f"{item} ({calories} kcal)", key=f"dinner_{item}"):
                if item == "Other":
                    custom_food = st.text_input("Dinner item", key="dinner_custom")
                    custom_cal = st.number_input("Dinner calories", min_value=0, step=10, key="dinner_custom_cal")
                    if custom_food:
                        total_calories += custom_cal
                else:
                    total_calories += calories

        st.success(f"Total estimated calories: {int(total_calories)} kcal")
        st.button("Save Meal Log")

with tab_workout:
    st.header("Workout Split")
    st.write(f"Today: **{loop_day_name}**")

    today_workout = WORKOUT_DETAILS.get(loop_day_name, [])
    total_volume = 0

    if not today_workout:
        st.info("Rest Day")
    else:
        st.subheader("Routine")
        for index, exercise in enumerate(today_workout):
            st.markdown(f"**{exercise['name']}**")
            if exercise["sets_reps"]:
                st.caption(exercise["sets_reps"])
            if exercise["description"]:
                st.write(exercise["description"])
            render_steps(exercise.get("steps", []))

            completed = st.checkbox("Done", key=f"done_{loop_day_name}_{index}")
            sets, reps = parse_sets_reps(exercise.get("sets_reps", ""))
            sets_value = st.number_input(
                "Sets", min_value=0, value=sets, step=1, key=f"sets_{loop_day_name}_{index}"
            )
            reps_value = st.number_input(
                "Reps", min_value=0, value=reps, step=1, key=f"reps_{loop_day_name}_{index}"
            )
            weight_value = st.number_input(
                "Weight (kg)", min_value=0.0, value=0.0, step=2.5, key=f"weight_{loop_day_name}_{index}"
            )
            if completed and sets_value and reps_value:
                total_volume += weight_value * sets_value * reps_value

            if exercise["link"]:
                st.link_button("Watch Form", exercise["link"])
            wger_image = get_wger_image(exercise.get("name", ""))
            if wger_image:
                st.image(wger_image, use_column_width=True)
            else:
                st.image(get_youtube_thumbnail(exercise.get("link", "")), use_column_width=True)
            st.divider()

    st.subheader("Add Exercise")
    custom_name = st.text_input("Exercise name", key="custom_exercise_name")
    custom_sets = st.number_input("Sets", min_value=0, step=1, key="custom_exercise_sets")
    custom_reps = st.number_input("Reps", min_value=0, step=1, key="custom_exercise_reps")
    custom_weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, key="custom_exercise_weight")
    custom_done = st.checkbox("Done", key="custom_exercise_done")
    if custom_done and custom_sets and custom_reps:
        total_volume += custom_weight * custom_sets * custom_reps

    st.subheader("Workout Summary")
    body_weight = st.number_input("Body weight (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.5)
    workout_minutes = st.number_input("Workout duration (minutes)", min_value=0, value=60, step=5)
    calories = calories_burned(body_weight, workout_minutes)
    st.success(f"Estimated calories burned: {int(calories)} kcal")
    st.info(f"Total volume moved: {int(total_volume)} kg")

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
