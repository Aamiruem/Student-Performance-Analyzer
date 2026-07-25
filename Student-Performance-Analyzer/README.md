# Student Performance Analyzer

A Streamlit project for analyzing student performance from a CSV dataset.

## Features

- CSV upload and column validation
- Score, attendance, pass-rate, and student-count KPIs
- Performance-distribution charts
- Study-hours versus final-score analysis
- Filters for performance level, gender, and score
- Individual student reports and recommendations
- New-student form
- Filtered and updated CSV downloads

## Project files

```text
Student-Performance-Analyzer/
├── app.py
├── StudentPerformance.csv
├── requirements.txt
└── README.md
```

## Run on Windows PowerShell

Open PowerShell inside this project folder, then run:

```powershell
conda create -n student-analyzer python=3.11 -y
conda activate student-analyzer
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit will display a local address such as:

```text
http://localhost:8501
```

Open that address in your browser if it does not open automatically.

## CSV columns

The included dataset contains:

- `student_id`
- `gender`
- `age`
- `study_hours_per_week`
- `attendance_percentage`
- `previous_score`
- `assignments_completed`
- `sleep_hours_per_day`
- `internet_access`
- `extracurricular_activities`
- `parental_education`
- `tutoring`
- `final_score`
- `performance_level`

The sample data is synthetic and intended for learning, visualization, and
machine-learning practice.
