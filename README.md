# Student Performance Prediction System

Machine Learning Capstone Project (SkillOrbit). A machine learning application that analyzes student
academic data, predicts performance (Low / Average / High and a numeric final score), identifies the
key factors behind performance, shows a dashboard, and generates improvement recommendations.

## Project structure

| File | Purpose |
|---|---|
| `generate_dataset.py` | Creates the self-created academic dataset (1,000 students + injected missing values/duplicates) |
| `ml_core.py` | Shared logic: cleaning, feature encoding, performance levels, recommendations, prediction helper |
| `train_model.py` | Module 1-3: preprocessing, EDA charts, model training and evaluation, saves model + metrics |
| `app.py` | Module 4-5: Streamlit dashboard and recommendation system |
| `data/` | Raw, cleaned and predictions CSVs |
| `models/model_bundle.joblib` | Trained regressor + classifier |
| `outputs/` | `metrics.json`, `test_predictions.csv`, `figures/` |

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python generate_dataset.py      # creates data/student_performance_raw.csv
python train_model.py           # cleans data, makes charts, trains models, saves outputs
streamlit run app.py            # opens the dashboard at http://localhost:8501
```

## Using a real dataset instead

To use the Kaggle "Student Performance" dataset, map its columns onto the names used here
(`attendance`, `study_hours`, `internal_marks`, `participation`, `previous_score`, `final_score`, ...) and save it as
`data/student_performance_raw.csv`, then run `train_model.py`. Edit `NUMERIC`, `CATEGORICAL` and `SUBJECTS`
in `ml_core.py` if your columns differ.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository (include `data/`, `models/` and `outputs/metrics.json`, or let the app rebuild them on first run: `app.py` does this automatically).
2. Go to https://share.streamlit.io, click **New app**, pick the repo, branch and `app.py`.
3. Deploy, then paste the public URL into your report's "Deployment Link".

## Method summary

* **Preprocessing:** drop duplicates, median imputation (numeric), mode imputation (categorical), one-hot encoding, standard scaling inside a scikit-learn `Pipeline`.
* **Targets:** `final_score` (regression) and `performance_level` (Low < 50, Average 50-66.9, High >= 67).
* **Models:** Linear Regression, Decision Tree, Random Forest (evaluated with an 80/20 split and 5-fold cross-validation).
* **Recommendations:** rule-based, compares each student with the median of the High-performing group.
