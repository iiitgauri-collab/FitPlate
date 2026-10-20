
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(
    page_title="FitPlate",
    page_icon="🥗"
)

# STEP A: Create our notebook (database)
def create_database():
    conn = sqlite3.connect("fitplate.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            duration INTEGER
        )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT UNIQUE,
        meal TEXT,
        calories INTEGER,
        water INTEGER,
        energy INTEGER,
        weight REAL
    )
    """)
    conn.commit()
    conn.close()


create_database()

# STEP B: Show the app title
st.title("🥗 FitPlate")
st.write("Welcome to your fitness companion!")

# STEP C: Create the menu
page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Log Workout",
        "Nutrition Tracker",
        "History & Reminders"
    ]
)

# STEP D: Workout form
if page == "Log Workout":

    st.header("💪 Log Your Workout")

    name = st.text_input("Your Name")

    exercise = st.selectbox(
        "Choose Exercise",
        ["Walking", "Running", "Cycling", "Push-ups", "Squats"]
    )

    sets = st.number_input(
        "Number of Sets", min_value=1, value=3
    )

    reps = st.number_input(
        "Repetitions", min_value=1, value=10
    )

    duration = st.number_input(
        "Duration (minutes)", min_value=1, value=30
    )

    # STEP E: Save button
    if st.button("Save Workout"):

        if name.strip() == "":
            st.error("Please enter your name.")

        else:
            conn = sqlite3.connect("fitplate.db")

            conn.execute("""
                INSERT INTO workouts
                (name, exercise, sets, reps, duration)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                exercise,
                int(sets),
                int(reps),
                int(duration)
            ))

            conn.commit()
            conn.close()

            st.success("Your workout has been saved!")


elif page == "Dashboard":

    st.header("📊 My Fitness Dashboard")

    # Read workout information from the database
    conn = sqlite3.connect("fitplate.db")

    workouts = pd.read_sql_query(
        "SELECT * FROM workouts",
        conn
    )

    nutrition = pd.read_sql_query(
        "SELECT * FROM nutrition",
        conn
    )

    conn.close()

    # Calculate workout statistics
    if not workouts.empty:

        total_workouts = len(workouts)

        total_repetitions = int(
            (workouts["sets"] * workouts["reps"]).sum()
        )

        total_minutes = int(workouts["duration"].sum())

    else:
        total_workouts = 0
        total_repetitions = 0
        total_minutes = 0

    # Calculate nutrition statistics
    if not nutrition.empty:

        total_calories = int(
            nutrition["calories"].sum()
        )

        total_water = int(
            nutrition["water"].sum()
        )

    else:
        total_calories = 0
        total_water = 0

    # Display summary cards
    st.subheader("🏆 My Activity Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Workout Records",
        total_workouts
    )

    col2.metric(
        "Total Repetitions",
        f"{total_repetitions:,}"
    )

    col3.metric(
        "Workout Minutes",
        total_minutes
    )

    st.divider()

    st.subheader("🍎 My Nutrition Summary")

    col4, col5 = st.columns(2)

    col4.metric(
        "Calories Logged",
        f"{total_calories:,} kcal"
    )

    col5.metric(
        "Water Logged",
        f"{total_water:,} ml"
    )

    # Show workout chart
    st.divider()

    st.subheader("💪 Exercise Records")

    if not workouts.empty:

        exercise_counts = (
            workouts["exercise"].value_counts()
        )

        st.bar_chart(exercise_counts)

    else:
        st.info(
            "No workouts yet. Go to Log Workout "
            "and add your first exercise."
        )

    # Show weight chart
    st.subheader("⚖️ Weight Progress")

    if not nutrition.empty:

        weight_data = nutrition[
            nutrition["weight"].notna()
            & (nutrition["weight"] > 0)
        ]

        if not weight_data.empty:

            weight_data = weight_data.sort_values(
                "log_date"
            )

            weight_chart = weight_data.set_index(
                "log_date"
            )["weight"]

            st.line_chart(weight_chart)

        else:
            st.info(
                "Enter your weight in Nutrition Tracker "
                "to see your progress chart."
            )

    else:
        st.info(
            "Save a nutrition record to begin tracking."
        )
        
elif page == "Nutrition Tracker":

    st.header("🍎 Daily Nutrition Tracker")

    st.write("Record your food and daily habits.")

    # Ask the user for information
    log_date = st.date_input(
        "Choose Date",
        value=__import__("datetime").date.today(),
        key="nutrition_date"
    )

    meal = st.text_area(
        "What did you eat today?",
        placeholder="Example: Rice, dal, vegetables"
    )

    calories = st.number_input(
        "Estimated Calories (kcal)",
        min_value=0,
        max_value=10000,
        value=0
    )

    water = st.number_input(
        "Water Intake (ml)",
        min_value=0,
        max_value=15000,
        value=0,
        step=250
    )

    energy = st.slider(
        "How energetic do you feel?",
        min_value=1,
        max_value=5,
        value=3
    )

    weight = st.number_input(
        "Weight in kg (enter 0 to skip)",
        min_value=0.0,
        max_value=500.0,
        value=0.0,
        step=0.1
    )

    # Save the information
    if st.button("Save Nutrition Record"):

        conn = sqlite3.connect("fitplate.db")

        conn.execute("""
            INSERT INTO nutrition
            (log_date, meal, calories, water, energy, weight)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(log_date) DO UPDATE SET
                meal = excluded.meal,
                calories = excluded.calories,
                water = excluded.water,
                energy = excluded.energy,
                weight = excluded.weight
        """, (
            log_date.isoformat(),
            meal,
            int(calories),
            int(water),
            int(energy),
            weight if weight > 0 else None
        ))

        conn.commit()
        conn.close()

        st.success("Nutrition record saved successfully!")