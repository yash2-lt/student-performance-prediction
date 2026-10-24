import numpy as np
import pandas as pd

LOW_CUTOFF = 50
HIGH_CUTOFF = 67
LEVELS = ["Low", "Average", "High"]

CATEGORICAL = ["gender", "parental_education", "internet_access", "extracurricular", "tutoring"]
NUMERIC = ["attendance", "study_hours", "internal_marks", "participation", "previous_score"]
SUBJECTS = ["math_score", "science_score", "english_score", "computer_score"]
TARGET_SCORE = "final_score"
TARGET_LEVEL = "performance_level"

def load_raw(path: str = "data/student_performance_raw.csv") -> pd.DataFrame:
    return pd.read_csv(path)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates().reset_index(drop=True)

    for col in NUMERIC:
        df[col] = df[col].fillna(df[col].median())
    for col in CATEGORICAL:
        df[col] = df[col].fillna(df[col].mode()[0])
    return df

def to_level(score: float) -> str:
    if score < LOW_CUTOFF:
        return "Low"
    if score >= HIGH_CUTOFF:
        return "High"
    return "Average"

def add_performance_level(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[TARGET_LEVEL] = df[TARGET_SCORE].apply(to_level)
    return df

def build_features(df: pd.DataFrame, columns=None):
    X = pd.get_dummies(df[NUMERIC + CATEGORICAL], columns=CATEGORICAL, drop_first=False, dtype=int)
    if columns is not None:
        X = X.reindex(columns=columns, fill_value=0)
    return X

def generate_recommendations(student: dict, df_ref: pd.DataFrame) -> list:
    high = df_ref[df_ref[TARGET_LEVEL] == "High"]
    bench_att = high["attendance"].median()
    bench_study = high["study_hours"].median()
    bench_part = high["participation"].median()
    bench_internal = high["internal_marks"].median()

    recs = []
    if student["attendance"] < 75:
        recs.append(f"Improve attendance: currently {student['attendance']:.0f}%, high performers "
                    f"typically attend about {bench_att:.0f}%. Aim for at least 75% first.")
    elif student["attendance"] < bench_att:
        recs.append(f"Attendance is acceptable ({student['attendance']:.0f}%) but pushing towards "
                    f"{bench_att:.0f}% matches the high-performing group.")

    if student["study_hours"] < bench_study - 0.5:
        gap = bench_study - student["study_hours"]
        recs.append(f"Increase study hours: add about {gap:.1f} hours per day "
                    f"(currently {student['study_hours']:.1f}, high performers study about {bench_study:.1f}).")

    if student["participation"] < bench_part - 0.5:
        recs.append("Participate more in class discussions, labs and group activities.")

    if student["internal_marks"] < bench_internal - 5:
        recs.append("Internal marks are below the high-performer benchmark: revise regularly and "
                    "attend practice sessions before internal assessments.")

    subj = {s: student[s] for s in SUBJECTS if s in student and pd.notna(student[s])}
    if subj:
        avg = np.mean(list(subj.values()))
        weak = [s.replace("_score", "").title() for s, v in subj.items() if v < avg - 5]
        lowest = min(subj, key=subj.get)
        if not weak and subj[lowest] < 50:
            weak = [lowest.replace("_score", "").title()]
        if weak:
            recs.append("Focus on weak subjects: " + ", ".join(weak) + ".")

    if student.get("tutoring") == "No" and student["internal_marks"] < 60:
        recs.append("Consider joining tutoring or peer-study sessions.")
    if student.get("internet_access") == "No":
        recs.append("Use college/library resources to get regular access to online learning material.")

    if not recs:
        recs.append("Great work! Keep up the current routine and continue attending practice sessions.")
    return recs

def predict_student(bundle: dict, student: dict):
    row = pd.DataFrame([student])
    X = build_features(row, bundle["columns"])
    score = float(np.clip(bundle["regressor"].predict(X)[0], 0, 100))
    level = bundle["classifier"].predict(X)[0]
    proba = dict(zip(bundle["classifier"].classes_, bundle["classifier"].predict_proba(X)[0]))
    return score, level, proba
