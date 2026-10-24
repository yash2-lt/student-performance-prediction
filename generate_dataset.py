import numpy as np
import pandas as pd

SEED = 42
N_STUDENTS = 1000

def generate(n: int = N_STUDENTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    student_id = [f"STU{str(i).zfill(4)}" for i in range(1, n + 1)]
    gender = rng.choice(["Male", "Female"], n)
    parental_education = rng.choice(
        ["High School", "Bachelors", "Masters", "PhD"], n, p=[0.35, 0.40, 0.18, 0.07]
    )
    internet_access = rng.choice(["Yes", "No"], n, p=[0.88, 0.12])
    extracurricular = rng.choice(["Yes", "No"], n, p=[0.55, 0.45])
    tutoring = rng.choice(["Yes", "No"], n, p=[0.30, 0.70])

    ability = rng.normal(0, 1, n)

    attendance = np.clip(78 + 8 * ability + rng.normal(0, 9, n), 35, 100)
    study_hours = np.clip(3.2 + 1.1 * ability + rng.normal(0, 1.3, n), 0.2, 9.0)
    participation = np.clip(6.0 + 1.2 * ability + rng.normal(0, 1.5, n), 1, 10)
    previous_score = np.clip(66 + 11 * ability + rng.normal(0, 7, n), 20, 100)
    internal_marks = np.clip(
        0.45 * previous_score + 0.25 * attendance + 2.0 * study_hours + 1.2 * participation
        + rng.normal(0, 6, n) - 5,
        10, 100,
    )

    edu_bonus = pd.Series(parental_education).map(
        {"High School": 0, "Bachelors": 1.0, "Masters": 1.8, "PhD": 2.2}
    ).to_numpy()
    bonus = (
        edu_bonus
        + np.where(tutoring == "Yes", 2.0, 0)
        + np.where(internet_access == "Yes", 1.5, 0)
        + np.where(extracurricular == "Yes", 0.8, 0)
    )

    final_score = np.clip(
        0.30 * internal_marks
        + 0.25 * previous_score
        + 0.18 * attendance
        + 2.4 * study_hours
        + 0.9 * participation
        + bonus
        + rng.normal(0, 4.0, n)
        - 6,
        0, 100,
    )

    def subject(offset, spread):
        return np.clip(final_score + offset + rng.normal(0, spread, n), 0, 100)

    df = pd.DataFrame({
        "student_id": student_id,
        "gender": gender,
        "parental_education": parental_education,
        "internet_access": internet_access,
        "extracurricular": extracurricular,
        "tutoring": tutoring,
        "attendance": attendance.round(1),
        "study_hours": study_hours.round(1),
        "internal_marks": internal_marks.round(1),
        "participation": participation.round(1),
        "previous_score": previous_score.round(1),
        "math_score": subject(-3, 8).round(1),
        "science_score": subject(0, 7).round(1),
        "english_score": subject(2, 7).round(1),
        "computer_score": subject(3, 8).round(1),
        "final_score": final_score.round(1),
    })

    for col, frac in [("attendance", 0.03), ("study_hours", 0.04), ("internal_marks", 0.02),
                      ("participation", 0.03), ("parental_education", 0.02)]:
        idx = rng.choice(n, int(n * frac), replace=False)
        df.loc[idx, col] = np.nan

    dupes = df.sample(25, random_state=seed)
    df = pd.concat([df, dupes], ignore_index=True)
    return df

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    data = generate()
    data.to_csv("data/student_performance_raw.csv", index=False)
    print(f"Saved data/student_performance_raw.csv  shape={data.shape}")
    print("Missing values:\n", data.isna().sum()[data.isna().sum() > 0])
    print("Duplicate rows:", data.duplicated().sum())
