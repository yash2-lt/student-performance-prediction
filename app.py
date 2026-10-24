import json
import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

import ml_core as core

st.set_page_config(page_title="Student Performance Prediction System", page_icon="🎓", layout="wide")

COLORS = {"Low": "#e5484d", "Average": "#f5a623", "High": "#2e9e6b"}

@st.cache_resource(show_spinner="Preparing data and model (first run only)...")
def load_artifacts():
    if not (os.path.exists("models/model_bundle.joblib") and os.path.exists("data/student_performance_predictions.csv")):
        import subprocess, sys
        if not os.path.exists("data/student_performance_raw.csv"):
            subprocess.run([sys.executable, "generate_dataset.py"], check=True)
        subprocess.run([sys.executable, "train_model.py"], check=True)
    bundle = joblib.load("models/model_bundle.joblib")
    data = pd.read_csv("data/student_performance_predictions.csv")
    with open("outputs/metrics.json") as f:
        metrics = json.load(f)
    return bundle, data, metrics

bundle, data, metrics = load_artifacts()

st.title("🎓 Student Performance Prediction System")
st.caption("Analyze academic data, predict performance level, and get improvement recommendations.")

tab_over, tab_pred, tab_comp, tab_subj, tab_trend, tab_rec, tab_model = st.tabs([
    "Overview", "Predict a student", "Student comparison", "Subject-wise analysis",
    "Performance trends", "Recommendations", "Model details",
])

with tab_over:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", f"{len(data):,}")
    c2.metric("Average final score", f"{data['final_score'].mean():.1f}")
    c3.metric("Average attendance", f"{data['attendance'].mean():.1f}%")
    c4.metric("Average study hours/day", f"{data['study_hours'].mean():.1f}")

    left, right = st.columns(2)
    with left:
        st.subheader("Performance level distribution")
        counts = data["performance_level"].value_counts().reindex(core.LEVELS)
        fig, ax = plt.subplots(figsize=(5, 3.4))
        ax.bar(counts.index, counts.values, color=[COLORS[l] for l in counts.index])
        for i, v in enumerate(counts.values):
            ax.text(i, v + 5, str(v), ha="center")
        ax.set_ylabel("Students")
        st.pyplot(fig)
    with right:
        st.subheader("What drives performance?")
        imp = pd.Series(bundle["feature_importance"]).sort_values(ascending=False).head(8).iloc[::-1]
        fig, ax = plt.subplots(figsize=(5, 3.4))
        ax.barh(imp.index, imp.values, color="#5b5bd6")
        ax.set_xlabel("Random Forest importance")
        st.pyplot(fig)

    st.subheader("Correlation of factors with final score")
    corr = data[core.NUMERIC + [core.TARGET_SCORE]].corr()
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, ax=ax)
    st.pyplot(fig)

with tab_pred:
    st.subheader("Enter student details")
    with st.form("predict_form"):
        a, b, c = st.columns(3)
        attendance = a.slider("Attendance (%)", 30, 100, 78)
        study_hours = a.slider("Study hours per day", 0.0, 9.0, 3.0, 0.1)
        internal_marks = b.slider("Internal marks", 10, 100, 60)
        participation = b.slider("Participation (1-10)", 1, 10, 6)
        previous_score = c.slider("Previous academic score", 20, 100, 65)
        gender = c.selectbox("Gender", ["Male", "Female"])
        d, e, f = st.columns(3)
        parental_education = d.selectbox("Parental education", ["High School", "Bachelors", "Masters", "PhD"])
        internet_access = e.selectbox("Internet access", ["Yes", "No"])
        tutoring = f.selectbox("Tutoring", ["No", "Yes"])
        extracurricular = d.selectbox("Extracurricular activities", ["Yes", "No"])

        st.markdown("**Subject scores** (used for subject-wise recommendations)")
        s1, s2, s3, s4 = st.columns(4)
        math = s1.number_input("Math", 0, 100, 60)
        science = s2.number_input("Science", 0, 100, 62)
        english = s3.number_input("English", 0, 100, 65)
        computer = s4.number_input("Computer", 0, 100, 68)
        submitted = st.form_submit_button("Predict performance")

    if submitted:
        student = dict(attendance=attendance, study_hours=study_hours, internal_marks=internal_marks,
                       participation=participation, previous_score=previous_score, gender=gender,
                       parental_education=parental_education, internet_access=internet_access,
                       tutoring=tutoring, extracurricular=extracurricular, math_score=math,
                       science_score=science, english_score=english, computer_score=computer)
        score, level, proba = core.predict_student(bundle, student)

        r1, r2, r3 = st.columns(3)
        r1.metric("Predicted final score", f"{score:.1f} / 100")
        r2.metric("Predicted level", level)
        r3.metric("Confidence", f"{max(proba.values()) * 100:.0f}%")

        st.progress(min(max(score / 100, 0.0), 1.0))
        prob_df = pd.DataFrame({"Level": core.LEVELS, "Probability": [proba.get(l, 0) for l in core.LEVELS]})
        st.bar_chart(prob_df.set_index("Level"))

        st.subheader("Personalised recommendations")
        for r in core.generate_recommendations(student, data):
            st.markdown(f"- {r}")

with tab_comp:
    st.subheader("Compare students")
    ids = st.multiselect("Select 2-5 students", data["student_id"].tolist(),
                         default=data["student_id"].tolist()[:3], max_selections=5)
    if ids:
        sel = data[data["student_id"].isin(ids)]
        st.dataframe(sel[["student_id", "attendance", "study_hours", "internal_marks", "participation",
                          "previous_score", "final_score", "predicted_score", "performance_level",
                          "predicted_level"]], use_container_width=True)
        long = sel.melt(id_vars="student_id", value_vars=core.NUMERIC + ["final_score"],
                        var_name="factor", value_name="value")
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.barplot(data=long, x="factor", y="value", hue="student_id", ax=ax)
        ax.set_xlabel("")
        st.pyplot(fig)

    st.subheader("Actual vs predicted score (all students)")
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.scatter(data["final_score"], data["predicted_score"], s=10, alpha=.5, color="#5b5bd6")
    ax.plot([0, 100], [0, 100], "k--", lw=1)
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    st.pyplot(fig)

with tab_subj:
    st.subheader("Subject-wise analysis")
    level_filter = st.multiselect("Filter by performance level", core.LEVELS, default=core.LEVELS)
    sub = data[data["performance_level"].isin(level_filter)]
    avg = sub[core.SUBJECTS].mean().rename(lambda s: s.replace("_score", "").title())
    st.bar_chart(avg)
    by_level = data.groupby("performance_level")[core.SUBJECTS].mean().reindex(core.LEVELS)
    by_level.columns = [c.replace("_score", "").title() for c in by_level.columns]
    st.dataframe(by_level.round(1), use_container_width=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    melted = sub.melt(value_vars=core.SUBJECTS, var_name="Subject", value_name="Score")
    melted["Subject"] = melted["Subject"].str.replace("_score", "").str.title()
    sns.boxplot(data=melted, x="Subject", y="Score", color="#5b5bd6", ax=ax)
    st.pyplot(fig)

with tab_trend:
    st.subheader("How does each factor relate to the score?")
    factor = st.selectbox("Factor", core.NUMERIC, format_func=lambda s: s.replace("_", " ").title())
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.scatterplot(data=data, x=factor, y="final_score", hue="performance_level", palette=COLORS,
                    hue_order=core.LEVELS, alpha=.6, s=20, ax=ax)
    sns.regplot(data=data, x=factor, y="final_score", scatter=False, color="black", ax=ax)
    st.pyplot(fig)

    st.subheader("Average final score by binned " + factor.replace("_", " "))
    bins = pd.qcut(data[factor], 8, duplicates="drop")
    trend = data.groupby(bins, observed=True)["final_score"].mean()
    trend.index = [f"{i.left:.0f}-{i.right:.0f}" for i in trend.index]
    st.line_chart(trend)

    st.subheader("Effect of categorical factors on average final score")
    cat = st.selectbox("Category", ["tutoring", "internet_access", "extracurricular", "parental_education", "gender"])
    st.bar_chart(data.groupby(cat)["final_score"].mean())

with tab_rec:
    st.subheader("Recommendations for an existing student")
    sid = st.selectbox("Student ID", data["student_id"])
    row = data[data["student_id"] == sid].iloc[0].to_dict()
    st.write(f"**Actual score:** {row['final_score']:.1f} &nbsp; | &nbsp; **Predicted score:** "
             f"{row['predicted_score']:.1f} &nbsp; | &nbsp; **Level:** {row['predicted_level']}")
    for r in core.generate_recommendations(row, data):
        st.markdown(f"- {r}")

with tab_model:
    st.subheader("Model comparison")
    st.markdown("**Regression (predict final score)**")
    st.dataframe(pd.DataFrame(metrics["regression"]).T, use_container_width=True)
    st.markdown("**Classification (Low / Average / High)**")
    st.dataframe(pd.DataFrame(metrics["classification"]).T, use_container_width=True)
    st.info(f"Deployed models: **{bundle['reg_name']}** for score, **{bundle['clf_name']}** for level.")
    cm = pd.DataFrame(metrics["confusion_matrix"], index=[f"Actual {l}" for l in core.LEVELS],
                      columns=[f"Pred {l}" for l in core.LEVELS])
    st.markdown("**Confusion matrix (test set)**")
    st.dataframe(cm, use_container_width=True)
    st.caption("The dataset is synthetic (self-created) for demonstration. Predictions are decision support, "
               "not a final judgement of any student.")
