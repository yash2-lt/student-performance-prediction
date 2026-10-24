import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

import ml_core as core

RANDOM_STATE = 42
FIG = "outputs/figures"
os.makedirs(FIG, exist_ok=True)
os.makedirs("models", exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")
PALETTE = {"Low": "#e5484d", "Average": "#f5a623", "High": "#2e9e6b"}

metrics = {}

def save_fig(name):
    plt.tight_layout()
    plt.savefig(f"{FIG}/{name}.png", dpi=160)
    plt.close()

raw = core.load_raw()
metrics["raw_rows"], metrics["raw_cols"] = raw.shape
metrics["missing_before"] = {k: int(v) for k, v in raw.isna().sum().items() if v > 0}
metrics["duplicates_before"] = int(raw.duplicated().sum())

df = core.clean_data(raw)
df = core.add_performance_level(df)
metrics["clean_rows"] = int(df.shape[0])
metrics["missing_after"] = int(df.isna().sum().sum())
metrics["level_counts"] = df[core.TARGET_LEVEL].value_counts().reindex(core.LEVELS).to_dict()
metrics["score_summary"] = df[core.TARGET_SCORE].describe().round(2).to_dict()
df.to_csv("data/student_performance_clean.csv", index=False)
print(f"Raw {raw.shape} -> clean {df.shape}; duplicates removed={metrics['duplicates_before']}")

plt.figure(figsize=(6, 4))
order = core.LEVELS
ax = sns.countplot(data=df, x=core.TARGET_LEVEL, order=order, palette=PALETTE, hue=core.TARGET_LEVEL, legend=False)
for p in ax.patches:
    ax.annotate(int(p.get_height()), (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center", va="bottom", fontsize=10)
plt.title("Performance level distribution")
plt.xlabel("")
plt.ylabel("Students")
save_fig("01_level_distribution")

plt.figure(figsize=(6.5, 4))
sns.histplot(df[core.TARGET_SCORE], bins=30, kde=True, color="#5b5bd6")
plt.axvline(core.LOW_CUTOFF, color="#e5484d", ls="--", label=f"Low < {core.LOW_CUTOFF}")
plt.axvline(core.HIGH_CUTOFF, color="#2e9e6b", ls="--", label=f"High >= {core.HIGH_CUTOFF}")
plt.legend()
plt.title("Final score distribution")
plt.xlabel("Final score")
save_fig("02_score_distribution")

plt.figure(figsize=(8, 6))
corr_cols = core.NUMERIC + [core.TARGET_SCORE]
corr = df[corr_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0, square=True, cbar_kws={"shrink": .8})
plt.title("Correlation of numeric factors")
save_fig("03_correlation_heatmap")
metrics["corr_with_score"] = corr[core.TARGET_SCORE].drop(core.TARGET_SCORE).round(3).sort_values(ascending=False).to_dict()

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
for ax, col in zip(axes.ravel(), core.NUMERIC):
    sns.scatterplot(data=df, x=col, y=core.TARGET_SCORE, hue=core.TARGET_LEVEL, palette=PALETTE,
                    hue_order=core.LEVELS, alpha=.55, s=18, ax=ax, legend=(col == core.NUMERIC[0]))
    sns.regplot(data=df, x=col, y=core.TARGET_SCORE, scatter=False, color="black", line_kws={"lw": 1.5}, ax=ax)
    ax.set_title(f"{col.replace('_', ' ').title()} vs final score")
axes.ravel()[-1].axis("off")
save_fig("04_factors_vs_score")

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, col in zip(axes, ["attendance", "study_hours", "participation"]):
    sns.boxplot(data=df, x=core.TARGET_LEVEL, y=col, order=order, palette=PALETTE, hue=core.TARGET_LEVEL,
                legend=False, ax=ax)
    ax.set_title(f"{col.replace('_', ' ').title()} by performance level")
    ax.set_xlabel("")
save_fig("05_boxplots_by_level")

group_means = df.groupby(core.TARGET_LEVEL)[core.NUMERIC].mean().reindex(core.LEVELS).round(2)
metrics["group_means"] = group_means.to_dict(orient="index")

subj_avg = df.groupby(core.TARGET_LEVEL)[core.SUBJECTS].mean().reindex(core.LEVELS)
subj_avg.T.plot(kind="bar", figsize=(7.5, 4.2), color=[PALETTE[l] for l in core.LEVELS])
plt.title("Average subject score by performance level")
plt.ylabel("Average score")
plt.xticks(rotation=0)
plt.xticks(range(4), [s.replace("_score", "").title() for s in core.SUBJECTS])
save_fig("06_subject_wise")
metrics["subject_avg_overall"] = df[core.SUBJECTS].mean().round(2).to_dict()

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, col in zip(axes, ["tutoring", "internet_access", "parental_education"]):
    sns.barplot(data=df, x=col, y=core.TARGET_SCORE, ax=ax, color="#5b5bd6", errorbar=None)
    ax.set_title(f"Average final score by {col.replace('_', ' ')}")
    ax.set_xlabel("")
    ax.set_ylim(40, 85)
    ax.tick_params(axis="x", rotation=15)
save_fig("07_categorical_factors")
metrics["cat_effects"] = {
    c: df.groupby(c)[core.TARGET_SCORE].mean().round(2).to_dict()
    for c in ["tutoring", "internet_access", "extracurricular", "parental_education", "gender"]
}

X = core.build_features(df)
y_score = df[core.TARGET_SCORE]
y_level = df[core.TARGET_LEVEL]

X_tr, X_te, ys_tr, ys_te, yl_tr, yl_te = train_test_split(
    X, y_score, y_level, test_size=0.2, random_state=RANDOM_STATE, stratify=y_level
)
metrics["train_size"], metrics["test_size"] = int(len(X_tr)), int(len(X_te))

regressors = {
    "Linear Regression": Pipeline([("scale", StandardScaler()), ("m", LinearRegression())]),
    "Decision Tree": Pipeline([("scale", StandardScaler()),
                               ("m", DecisionTreeRegressor(max_depth=6, min_samples_leaf=10, random_state=RANDOM_STATE))]),
    "Random Forest": Pipeline([("scale", StandardScaler()),
                               ("m", RandomForestRegressor(n_estimators=300, max_depth=10, min_samples_leaf=3,
                                                           random_state=RANDOM_STATE, n_jobs=-1))]),
}
reg_results = {}
for name, pipe in regressors.items():
    pipe.fit(X_tr, ys_tr)
    pred = pipe.predict(X_te)
    cv = cross_val_score(pipe, X, y_score, cv=5, scoring="r2")
    reg_results[name] = {
        "MAE": round(mean_absolute_error(ys_te, pred), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(ys_te, pred))), 3),
        "R2": round(r2_score(ys_te, pred), 4),
        "CV_R2_mean": round(cv.mean(), 4),
        "CV_R2_std": round(cv.std(), 4),
    }
    print(f"[REG] {name:18s} {reg_results[name]}")
metrics["regression"] = reg_results
best_reg_name = max(reg_results, key=lambda k: reg_results[k]["R2"])
best_reg = regressors[best_reg_name]
metrics["best_regressor"] = best_reg_name

classifiers = {
    "Decision Tree": Pipeline([("scale", StandardScaler()),
                               ("m", DecisionTreeClassifier(max_depth=6, min_samples_leaf=10, random_state=RANDOM_STATE))]),
    "Random Forest": Pipeline([("scale", StandardScaler()),
                               ("m", RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_leaf=3,
                                                            random_state=RANDOM_STATE, n_jobs=-1))]),
}
clf_results = {}
for name, pipe in classifiers.items():
    pipe.fit(X_tr, yl_tr)
    pred = pipe.predict(X_te)
    cv = cross_val_score(pipe, X, y_level, cv=5, scoring="accuracy")
    clf_results[name] = {
        "Accuracy": round(accuracy_score(yl_te, pred), 4),
        "F1_macro": round(f1_score(yl_te, pred, average="macro"), 4),
        "CV_Accuracy_mean": round(cv.mean(), 4),
        "CV_Accuracy_std": round(cv.std(), 4),
    }
    print(f"[CLF] {name:18s} {clf_results[name]}")
metrics["classification"] = clf_results
best_clf_name = max(clf_results, key=lambda k: clf_results[k]["F1_macro"])
best_clf = classifiers[best_clf_name]
metrics["best_classifier"] = best_clf_name

pred_level = best_clf.predict(X_te)
metrics["classification_report"] = classification_report(yl_te, pred_level, labels=core.LEVELS, output_dict=True, zero_division=0)
cm = confusion_matrix(yl_te, pred_level, labels=core.LEVELS)
metrics["confusion_matrix"] = cm.tolist()

plt.figure(figsize=(5.5, 4.5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=core.LEVELS, yticklabels=core.LEVELS, cbar=False)
plt.title(f"Confusion matrix: {best_clf_name}")
plt.xlabel("Predicted")
plt.ylabel("Actual")
save_fig("08_confusion_matrix")

plt.figure(figsize=(5.8, 5))
pred_score = best_reg.predict(X_te)
plt.scatter(ys_te, pred_score, alpha=.55, s=18, color="#5b5bd6")
lims = [min(ys_te.min(), pred_score.min()) - 2, max(ys_te.max(), pred_score.max()) + 2]
plt.plot(lims, lims, "k--", lw=1)
plt.xlim(lims)
plt.ylim(lims)
plt.xlabel("Actual final score")
plt.ylabel("Predicted final score")
plt.title(f"Actual vs predicted: {best_reg_name}\nR² = {reg_results[best_reg_name]['R2']:.3f}")
save_fig("09_actual_vs_predicted")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
r2s = pd.Series({k: v["R2"] for k, v in reg_results.items()})
r2s.plot(kind="bar", ax=axes[0], color="#5b5bd6")
axes[0].set_title("Regression: R² on test set")
axes[0].set_ylim(0, 1)
axes[0].tick_params(axis="x", rotation=15)
for i, v in enumerate(r2s):
    axes[0].text(i, v + .01, f"{v:.3f}", ha="center")
f1s = pd.Series({k: v["F1_macro"] for k, v in clf_results.items()})
f1s.plot(kind="bar", ax=axes[1], color="#2e9e6b")
axes[1].set_title("Classification: macro F1 on test set")
axes[1].set_ylim(0, 1)
axes[1].tick_params(axis="x", rotation=15)
for i, v in enumerate(f1s):
    axes[1].text(i, v + .01, f"{v:.3f}", ha="center")
save_fig("10_model_comparison")

rf_clf = classifiers["Random Forest"].named_steps["m"]
imp = pd.Series(rf_clf.feature_importances_, index=X.columns).sort_values(ascending=False)
metrics["feature_importance"] = imp.head(10).round(4).to_dict()
plt.figure(figsize=(7, 5))
imp.head(10).iloc[::-1].plot(kind="barh", color="#5b5bd6")
plt.title("Top 10 factors affecting performance (Random Forest)")
plt.xlabel("Importance")
save_fig("11_feature_importance")

joblib.dump({"regressor": best_reg, "classifier": best_clf, "columns": list(X.columns),
             "reg_name": best_reg_name, "clf_name": best_clf_name,
             "feature_importance": imp.to_dict()}, "models/model_bundle.joblib")

preds = df.loc[X_te.index, ["student_id"]].copy()
preds["actual_score"] = ys_te.values
preds["predicted_score"] = pred_score.round(1)
preds["actual_level"] = yl_te.values
preds["predicted_level"] = pred_level
preds.to_csv("outputs/test_predictions.csv", index=False)

df_pred = df.copy()
df_pred["predicted_score"] = np.clip(best_reg.predict(X), 0, 100).round(1)
df_pred["predicted_level"] = best_clf.predict(X)
df_pred.to_csv("data/student_performance_predictions.csv", index=False)

samples = []
for lvl in core.LEVELS:
    sid = preds[preds["predicted_level"] == lvl]["student_id"].iloc[0]
    stu = df[df["student_id"] == sid].iloc[0].to_dict()
    score, level, proba = core.predict_student(joblib.load("models/model_bundle.joblib"), stu)
    samples.append({
        "student_id": sid, "predicted_score": round(score, 1), "predicted_level": level,
        "actual_score": float(stu["final_score"]),
        "attendance": stu["attendance"], "study_hours": stu["study_hours"],
        "recommendations": core.generate_recommendations(stu, df),
    })
metrics["sample_recommendations"] = samples

with open("outputs/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))

print("\nBest regressor :", best_reg_name, reg_results[best_reg_name])
print("Best classifier:", best_clf_name, clf_results[best_clf_name])
print("Saved models/model_bundle.joblib, outputs/metrics.json and figures.")
