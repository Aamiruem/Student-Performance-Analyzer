from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = APP_DIR / "StudentPerformance.csv"

REQUIRED_COLUMNS = [
    "student_id",
    "gender",
    "age",
    "study_hours_per_week",
    "attendance_percentage",
    "previous_score",
    "assignments_completed",
    "sleep_hours_per_day",
    "internet_access",
    "extracurricular_activities",
    "parental_education",
    "tutoring",
    "final_score",
    "performance_level",
]

NUMERIC_COLUMNS = [
    "age",
    "study_hours_per_week",
    "attendance_percentage",
    "previous_score",
    "assignments_completed",
    "sleep_hours_per_day",
    "final_score",
]

PERFORMANCE_ORDER = [
    "Needs Improvement",
    "Average",
    "Good",
    "Excellent",
]


def performance_level(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Average"
    return "Needs Improvement"


def clean_and_validate_data(data: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    cleaned = data[REQUIRED_COLUMNS].copy()

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=REQUIRED_COLUMNS)
    cleaned["student_id"] = cleaned["student_id"].astype(str).str.strip()
    cleaned["performance_level"] = cleaned["final_score"].apply(
        performance_level
    )

    return cleaned


@st.cache_data
def load_default_data() -> pd.DataFrame:
    return clean_and_validate_data(pd.read_csv(DEFAULT_DATA_FILE))


def next_student_id(data: pd.DataFrame) -> str:
    numeric_ids = (
        data["student_id"]
        .astype(str)
        .str.extract(r"(\d+)$", expand=False)
        .dropna()
    )

    if numeric_ids.empty:
        return "STU0001"

    next_number = numeric_ids.astype(int).max() + 1
    return f"STU{next_number:04d}"


def student_recommendations(student: pd.Series) -> list[str]:
    recommendations = []

    if student["attendance_percentage"] < 75:
        recommendations.append(
            "Improve attendance to at least 75% by following a regular class schedule."
        )

    if student["study_hours_per_week"] < 10:
        recommendations.append(
            "Increase focused study time to at least 10 hours per week."
        )

    if student["assignments_completed"] < 7:
        recommendations.append(
            "Complete more assignments because regular practice improves understanding."
        )

    if not 6 <= student["sleep_hours_per_day"] <= 8:
        recommendations.append(
            "Maintain 6–8 hours of sleep per day for better concentration."
        )

    if student["previous_score"] < 60:
        recommendations.append(
            "Revise weak subjects and practice previous examination questions."
        )

    if not recommendations:
        recommendations.append(
            "Performance habits are strong. Continue the current routine and set a higher goal."
        )

    return recommendations


st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="🎓",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #eef2ff, #f8fafc);
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 16px;
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            color: white;
            background: linear-gradient(120deg, #0f766e, #2563eb);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2rem;
        }
        .hero p {
            margin: 0.45rem 0 0;
            opacity: 0.92;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Student Performance Analyzer</h1>
        <p>Analyze academic performance, identify improvement areas, and explore student data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.sidebar.file_uploader(
    "Upload another student CSV",
    type=["csv"],
    help="The uploaded file must contain the same 14 columns as the sample dataset.",
)

try:
    if uploaded_file is None:
        data = load_default_data()
        st.sidebar.success("Using StudentPerformance.csv")
    else:
        data = clean_and_validate_data(pd.read_csv(uploaded_file))
        st.sidebar.success(f"Using {uploaded_file.name}")
except FileNotFoundError:
    st.error(
        "StudentPerformance.csv was not found. Keep it in the same folder as app.py."
    )
    st.stop()
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Could not load the CSV file: {error}")
    st.stop()

st.sidebar.header("Filters")

available_levels = [
    level
    for level in PERFORMANCE_ORDER
    if level in data["performance_level"].unique()
]
selected_levels = st.sidebar.multiselect(
    "Performance level",
    available_levels,
    default=available_levels,
)

gender_options = ["All"] + sorted(data["gender"].unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", gender_options)

minimum_score = float(data["final_score"].min())
maximum_score = float(data["final_score"].max())
selected_score_range = st.sidebar.slider(
    "Final-score range",
    min_value=minimum_score,
    max_value=maximum_score,
    value=(minimum_score, maximum_score),
    step=1.0,
)

filtered_data = data[
    data["performance_level"].isin(selected_levels)
    & data["final_score"].between(*selected_score_range)
].copy()

if selected_gender != "All":
    filtered_data = filtered_data[filtered_data["gender"] == selected_gender]

if filtered_data.empty:
    st.warning("No students match the selected filters.")
    st.stop()

total_students = len(filtered_data)
average_score = filtered_data["final_score"].mean()
average_attendance = filtered_data["attendance_percentage"].mean()
pass_rate = (filtered_data["final_score"] >= 60).mean() * 100

metric_columns = st.columns(4)
metric_columns[0].metric("Students", f"{total_students:,}")
metric_columns[1].metric("Average Score", f"{average_score:.1f}")
metric_columns[2].metric("Average Attendance", f"{average_attendance:.1f}%")
metric_columns[3].metric("Pass Rate", f"{pass_rate:.1f}%")

dashboard_tab, student_tab, data_tab, add_tab = st.tabs(
    [
        "Dashboard",
        "Student Analysis",
        "Data Table",
        "Add Student",
    ]
)

with dashboard_tab:
    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Performance Distribution")
        performance_counts = (
            filtered_data["performance_level"]
            .value_counts()
            .reindex(PERFORMANCE_ORDER, fill_value=0)
            .rename_axis("performance_level")
            .reset_index(name="students")
        )
        st.bar_chart(
            performance_counts,
            x="performance_level",
            y="students",
            color="#2563EB",
        )

    with right_chart:
        st.subheader("Average Score by Parental Education")
        education_scores = (
            filtered_data.groupby("parental_education", as_index=False)[
                "final_score"
            ]
            .mean()
            .sort_values("final_score")
        )
        st.bar_chart(
            education_scores,
            x="parental_education",
            y="final_score",
            color="#0F766E",
        )

    st.subheader("Study Hours Compared with Final Score")
    st.scatter_chart(
        filtered_data,
        x="study_hours_per_week",
        y="final_score",
        color="#7C3AED",
    )

    st.subheader("Top 10 Students")
    top_students = filtered_data.nlargest(10, "final_score")[
        [
            "student_id",
            "final_score",
            "attendance_percentage",
            "study_hours_per_week",
            "performance_level",
        ]
    ]
    st.dataframe(top_students, use_container_width=True, hide_index=True)

with student_tab:
    selected_student_id = st.selectbox(
        "Select student ID",
        sorted(filtered_data["student_id"].unique()),
    )
    student = filtered_data[
        filtered_data["student_id"] == selected_student_id
    ].iloc[0]

    st.subheader(f"Performance Report: {selected_student_id}")
    student_metrics = st.columns(4)
    student_metrics[0].metric("Final Score", f"{student['final_score']:.1f}")
    student_metrics[1].metric(
        "Attendance", f"{student['attendance_percentage']:.0f}%"
    )
    student_metrics[2].metric(
        "Study Hours", f"{student['study_hours_per_week']:.0f}/week"
    )
    student_metrics[3].metric(
        "Assignments", f"{student['assignments_completed']:.0f}/10"
    )

    detail_columns = st.columns(2)
    with detail_columns[0]:
        st.write("**Student details**")
        st.write(f"Age: {student['age']:.0f}")
        st.write(f"Gender: {student['gender']}")
        st.write(f"Previous score: {student['previous_score']:.1f}")
        st.write(f"Performance level: {student['performance_level']}")

    with detail_columns[1]:
        st.write("**Learning environment**")
        st.write(f"Internet access: {student['internet_access']}")
        st.write(f"Tutoring: {student['tutoring']}")
        st.write(
            "Extracurricular activities: "
            f"{student['extracurricular_activities']}"
        )
        st.write(f"Daily sleep: {student['sleep_hours_per_day']:.1f} hours")

    st.write("**Recommendations**")
    for recommendation in student_recommendations(student):
        st.info(recommendation)

with data_tab:
    st.subheader("Filtered Student Records")
    st.dataframe(filtered_data, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered CSV",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="FilteredStudentPerformance.csv",
        mime="text/csv",
    )

with add_tab:
    st.subheader("Add a New Student")
    st.caption(
        "The new row is added to a downloadable copy; the original CSV is not overwritten."
    )

    with st.form("new_student_form"):
        form_left, form_middle, form_right = st.columns(3)

        with form_left:
            new_id = st.text_input(
                "Student ID",
                value=next_student_id(data),
            )
            new_gender = st.selectbox(
                "Gender",
                ["Female", "Male", "Other"],
            )
            new_age = st.number_input(
                "Age",
                min_value=10,
                max_value=40,
                value=18,
            )
            new_study_hours = st.number_input(
                "Study hours per week",
                min_value=0,
                max_value=80,
                value=12,
            )
            new_attendance = st.number_input(
                "Attendance percentage",
                min_value=0,
                max_value=100,
                value=80,
            )

        with form_middle:
            new_previous_score = st.number_input(
                "Previous score",
                min_value=0.0,
                max_value=100.0,
                value=65.0,
                step=1.0,
            )
            new_assignments = st.number_input(
                "Assignments completed",
                min_value=0,
                max_value=10,
                value=7,
            )
            new_sleep = st.number_input(
                "Sleep hours per day",
                min_value=0.0,
                max_value=15.0,
                value=7.0,
                step=0.5,
            )
            new_internet = st.selectbox(
                "Internet access",
                ["Yes", "No"],
            )
            new_extracurricular = st.selectbox(
                "Extracurricular activities",
                ["Yes", "No"],
            )

        with form_right:
            new_parental_education = st.selectbox(
                "Parental education",
                ["High School", "Diploma", "Graduate", "Postgraduate"],
            )
            new_tutoring = st.selectbox(
                "Tutoring",
                ["No", "Yes"],
            )
            new_final_score = st.number_input(
                "Final score",
                min_value=0.0,
                max_value=100.0,
                value=70.0,
                step=1.0,
            )

        submitted = st.form_submit_button("Prepare student record")

    if submitted:
        normalized_id = new_id.strip()

        if not normalized_id:
            st.error("Student ID cannot be empty.")
        elif normalized_id in data["student_id"].astype(str).values:
            st.error("This student ID already exists. Enter a unique ID.")
        else:
            new_record = pd.DataFrame(
                [
                    {
                        "student_id": normalized_id,
                        "gender": new_gender,
                        "age": new_age,
                        "study_hours_per_week": new_study_hours,
                        "attendance_percentage": new_attendance,
                        "previous_score": new_previous_score,
                        "assignments_completed": new_assignments,
                        "sleep_hours_per_day": new_sleep,
                        "internet_access": new_internet,
                        "extracurricular_activities": new_extracurricular,
                        "parental_education": new_parental_education,
                        "tutoring": new_tutoring,
                        "final_score": new_final_score,
                        "performance_level": performance_level(new_final_score),
                    }
                ]
            )
            updated_data = pd.concat([data, new_record], ignore_index=True)
            st.success(
                f"{normalized_id} is ready. Download the updated dataset below."
            )
            st.dataframe(new_record, use_container_width=True, hide_index=True)
            st.download_button(
                "Download updated StudentPerformance.csv",
                data=updated_data.to_csv(index=False).encode("utf-8"),
                file_name="StudentPerformance_updated.csv",
                mime="text/csv",
            )
