const pptxgen = require("pptxgenjs");
const fs = require("fs");
const M = JSON.parse(fs.readFileSync("outputs/metrics.json", "utf8"));
const FIG = "outputs/figures/";

const INDIGO = "2B1B7A", INK = "1F1A3D", MUTED = "5F5B7A", TINT = "F1EEFC", WHITE = "FFFFFF";
const RED = "E5484D", AMBER = "F5A623", GREEN = "2E9E6B", TEAL = "1C9AB5";
const HEAD = "Cambria", BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "Student Performance Prediction System";
pres.author = "[Your Name]";

let n = 0;
function content(title) {
  const s = pres.addSlide();
  n++;
  s.background = { color: WHITE };
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: INDIGO, margin: 0, isTextBox: true, valign: "middle" });
  s.addText(String(n), { x: 9.2, y: 5.2, w: 0.4, h: 0.3, fontFace: BODY, fontSize: 10, color: MUTED, align: "right", margin: 0, isTextBox: true });
  return s;
}
function card(s, x, y, w, h, head, body, headColor) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.12 });
  s.addText(head, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.4, fontFace: HEAD, fontSize: 16, bold: true, color: headColor || INDIGO, margin: 0, isTextBox: true });
  s.addText(body, { x: x + 0.2, y: y + 0.6, w: w - 0.4, h: h - 0.75, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
}
function stat(s, x, y, w, big, label, color) {
  s.addText(big, { x, y, w, h: 0.9, fontFace: HEAD, fontSize: 44, bold: true, color: color || INDIGO, margin: 0, align: "left", isTextBox: true });
  s.addText(label, { x, y: y + 0.9, w, h: 0.5, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
}

// 1 ------------------------------------------------------------------ title
{
  const s = pres.addSlide(); n++;
  s.background = { color: INDIGO };
  s.addText("MACHINE LEARNING CAPSTONE PROJECT", { x: 0.7, y: 1.2, w: 8.6, h: 0.4, fontFace: BODY, fontSize: 14, color: "C9C2F5", charSpacing: 4, margin: 0, isTextBox: true });
  s.addText("Student Performance Prediction System", { x: 0.7, y: 1.7, w: 8.6, h: 1.5, fontFace: HEAD, fontSize: 44, bold: true, color: WHITE, margin: 0, valign: "top", isTextBox: true });
  s.addText("Predict Low, Average or High performance, find the factors behind it, and recommend how to improve", { x: 0.7, y: 3.3, w: 7.6, h: 0.8, fontFace: BODY, fontSize: 18, color: "E4E0FA", margin: 0, valign: "top", isTextBox: true });
  s.addText("[Your Name]  |  [Roll No.]  |  SkillOrbit", { x: 0.7, y: 4.7, w: 8, h: 0.4, fontFace: BODY, fontSize: 14, color: "C9C2F5", margin: 0, isTextBox: true });
  // level motif
  [[RED, "Low"], [AMBER, "Average"], [GREEN, "High"]].forEach(([c, t], i) => {
    s.addShape(pres.shapes.OVAL, { x: 8.2 + i * 0.45, y: 0.55, w: 0.35, h: 0.35, fill: { color: c }, line: { color: c } });
  });
}

// 2 ------------------------------------------------------------------ problem
{
  const s = content("Why predict student performance?");
  card(s, 0.5, 1.2, 2.8, 2.7, "The problem", "Struggling students are usually noticed only after final results, when it is too late to help.", RED);
  card(s, 3.6, 1.2, 2.8, 2.7, "The solution", "A machine learning system that analyzes academic data and predicts performance early.", INDIGO);
  card(s, 6.7, 1.2, 2.8, 2.7, "The outcome", "Predicted score and level, key factors, a dashboard, and personalised recommendations.", GREEN);
}

// 3 ------------------------------------------------------------------ workflow
{
  const s = content("End-to-end workflow");
  const steps = ["Dataset collection", "Data cleaning", "Exploratory analysis", "Model development", "Prediction generation", "Dashboard", "Advice engine"];
  const w = 1.15, gap = 0.16;
  steps.forEach((t, i) => {
    const x = 0.5 + i * (w + gap);
    s.addShape(pres.shapes.OVAL, { x: x + w / 2 - 0.3, y: 1.5, w: 0.6, h: 0.6, fill: { color: INDIGO }, line: { color: INDIGO } });
    s.addText(String(i + 1), { x: x + w / 2 - 0.3, y: 1.5, w: 0.6, h: 0.6, fontFace: HEAD, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(t, { x, y: 2.3, w, h: 0.8, fontFace: BODY, fontSize: 14, color: INK, align: "center", valign: "top", margin: 0, isTextBox: true });
  });
  s.addText("Modules 1-5 of the brief map onto this flow: preprocessing, EDA, prediction model, dashboard and recommendation system.", { x: 0.5, y: 3.8, w: 9, h: 0.8, fontFace: BODY, fontSize: 16, color: MUTED, margin: 0, isTextBox: true });
}

// 4 ------------------------------------------------------------------ data + stack
{
  const s = content("Dataset and tech stack");
  card(s, 0.5, 1.2, 4.4, 3.2, "Dataset (self-created, synthetic)",
    [{ text: `${M.clean_rows.toLocaleString()} students, ${M.raw_cols} columns`, options: { bullet: true, breakLine: true } },
     { text: "Attendance, study hours, internal marks, participation, previous score", options: { bullet: true, breakLine: true } },
     { text: "Background: gender, parental education, internet, tutoring, activities", options: { bullet: true, breakLine: true } },
     { text: "4 subject scores and the final score", options: { bullet: true } }]);
  card(s, 5.1, 1.2, 4.4, 3.2, "Tech stack",
    [{ text: "Python, Pandas, NumPy", options: { bullet: true, breakLine: true } },
     { text: "Scikit-learn (models, pipelines)", options: { bullet: true, breakLine: true } },
     { text: "Matplotlib and Seaborn (charts)", options: { bullet: true, breakLine: true } },
     { text: "Streamlit dashboard", options: { bullet: true, breakLine: true } },
     { text: "Streamlit Cloud deployment", options: { bullet: true } }]);
}

// 5 ------------------------------------------------------------------ preprocessing
{
  const s = content("Module 1: Data preprocessing");
  const missingTotal = Object.values(M.missing_before).reduce((a, b) => a + b, 0);
  stat(s, 0.5, 1.2, 2.1, `${M.raw_rows.toLocaleString()}`, "raw records");
  stat(s, 2.8, 1.2, 2.1, `${M.duplicates_before}`, "duplicates removed", RED);
  stat(s, 5.1, 1.2, 2.1, `${missingTotal}`, "missing values filled", AMBER);
  stat(s, 7.4, 1.2, 2.1, `${M.missing_after}`, "missing after cleaning", GREEN);
  s.addText([
    { text: "Median imputation for numeric columns, mode for categorical", options: { bullet: true, breakLine: true } },
    { text: "One-hot encoding of categorical data", options: { bullet: true, breakLine: true } },
    { text: "StandardScaler inside the model pipeline (fit on training data only)", options: { bullet: true, breakLine: true } },
    { text: "Subject and final scores kept out of the inputs to avoid leakage", options: { bullet: true } },
  ], { x: 0.5, y: 3.0, w: 9, h: 1.9, fontFace: BODY, fontSize: 16, color: INK, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
}

// 6 ------------------------------------------------------------------ EDA 1
{
  const s = content("Module 2: Class balance and score spread");
  s.addImage({ path: FIG + "01_level_distribution.png", x: 0.5, y: 1.2, w: 4.4, h: 2.93 });
  s.addImage({ path: FIG + "02_score_distribution.png", x: 5.1, y: 1.2, w: 4.4, h: 2.71 });
  const L = M.level_counts;
  s.addText(`Low ${L.Low}, Average ${L.Average}, High ${L.High}: a usable, reasonably balanced three-class problem. Mean score ${M.score_summary.mean.toFixed(1)}, std ${M.score_summary.std.toFixed(1)}.`,
    { x: 0.5, y: 4.3, w: 9, h: 0.7, fontFace: BODY, fontSize: 16, color: INK, margin: 0, valign: "top", isTextBox: true });
}

// 7 ------------------------------------------------------------------ EDA 2 correlation
{
  const s = content("Every academic factor moves with the score");
  s.addImage({ path: FIG + "03_correlation_heatmap.png", x: 0.5, y: 1.15, w: 4.6, h: 3.45 });
  const c = M.corr_with_score;
  const rows = Object.entries(c);
  s.addText("Correlation with final score", { x: 5.4, y: 1.2, w: 4.1, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: INDIGO, margin: 0, isTextBox: true });
  rows.forEach(([k, v], i) => {
    const y = 1.75 + i * 0.58;
    s.addText(k.replace("_", " "), { x: 5.4, y, w: 1.7, h: 0.4, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "middle", isTextBox: true });
    s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: y + 0.07, w: 2.0 * v, h: 0.26, fill: { color: INDIGO }, line: { color: INDIGO } });
    s.addText(v.toFixed(2), { x: 7.1 + 2.0 * v + 0.08, y, w: 0.6, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, valign: "middle", isTextBox: true });
  });
}

// 8 ------------------------------------------------------------------ High vs Low
{
  const s = content("What separates High from Low performers");
  const g = M.group_means;
  const hdr = ["Level", "Attendance %", "Study hrs/day", "Internal marks", "Participation", "Previous score"].map(t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: INDIGO }, fontFace: BODY, fontSize: 14, align: "center" } }));
  const rows = ["Low", "Average", "High"].map((l, i) => {
    const col = [RED, AMBER, GREEN][i];
    return [
      { text: l, options: { bold: true, color: col, fontFace: BODY, fontSize: 14, align: "center" } },
      ...["attendance", "study_hours", "internal_marks", "participation", "previous_score"].map(k => ({ text: g[l][k].toFixed(1), options: { fontFace: BODY, fontSize: 14, align: "center", color: INK, fill: { color: i % 2 ? TINT : WHITE } } })),
    ];
  });
  s.addTable([hdr, ...rows], { x: 0.5, y: 1.3, w: 9, colW: [1.4, 1.5, 1.5, 1.6, 1.5, 1.5], rowH: 0.5, border: { type: "solid", color: "D9D4F0", pt: 1 } });
  const dAtt = g.High.attendance - g.Low.attendance, dStudy = g.High.study_hours - g.Low.study_hours;
  s.addText(`High performers attend about ${dAtt.toFixed(0)} points more of their classes and study about ${dStudy.toFixed(1)} hours more each day than Low performers.`,
    { x: 0.5, y: 3.6, w: 9, h: 0.9, fontFace: BODY, fontSize: 18, color: INK, margin: 0, valign: "top", isTextBox: true });
}

// 9 ------------------------------------------------------------------ subjects
{
  const s = content("Subject-wise analysis");
  s.addImage({ path: FIG + "06_subject_wise.png", x: 0.5, y: 1.15, w: 5.4, h: 3.0 });
  const a = M.subject_avg_overall;
  s.addText("Average scores", { x: 6.3, y: 1.2, w: 3.2, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: INDIGO, margin: 0, isTextBox: true });
  Object.entries(a).forEach(([k, v], i) => {
    s.addText([{ text: k.replace("_score", "").replace(/^./, c => c.toUpperCase()) + "  ", options: { color: INK } }, { text: v.toFixed(1), options: { bold: true, color: INDIGO } }],
      { x: 6.3, y: 1.75 + i * 0.5, w: 3.2, h: 0.4, fontFace: BODY, fontSize: 16, margin: 0, isTextBox: true });
  });
  s.addText("Math is the weakest subject and Computer the strongest, at every performance level.", { x: 6.3, y: 3.8, w: 3.2, h: 1.0, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
}

// 10 ----------------------------------------------------------------- models
{
  const s = content("Module 3: Model comparison");
  const reg = M.regression, clf = M.classification;
  s.addText("Predict the score (R², higher is better)", { x: 0.5, y: 1.1, w: 4.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addChart(pres.charts.BAR, [{ name: "R2", labels: Object.keys(reg), values: Object.values(reg).map(v => v.R2) }], {
    x: 0.5, y: 1.45, w: 4.4, h: 2.7, barDir: "col", chartColors: [INDIGO], showLegend: false, showValue: true, dataLabelPosition: "outEnd",
    dataLabelFontFace: BODY, dataLabelFontSize: 12, dataLabelColor: INK, dataLabelFormatCode: "0.000",
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, catAxisLabelColor: INK, valAxisLabelFontFace: BODY, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED,
    valAxisMinVal: 0, valAxisMaxVal: 1, valGridLine: { color: "E6E2F5", size: 0.5 }, catGridLine: { style: "none" },
  });
  s.addText("Predict the level (macro F1)", { x: 5.1, y: 1.1, w: 4.4, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addChart(pres.charts.BAR, [{ name: "F1", labels: Object.keys(clf), values: Object.values(clf).map(v => v.F1_macro) }], {
    x: 5.1, y: 1.45, w: 4.4, h: 2.7, barDir: "col", chartColors: [GREEN], showLegend: false, showValue: true, dataLabelPosition: "outEnd",
    dataLabelFontFace: BODY, dataLabelFontSize: 12, dataLabelColor: INK, dataLabelFormatCode: "0.000",
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11, catAxisLabelColor: INK, valAxisLabelFontFace: BODY, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED,
    valAxisMinVal: 0, valAxisMaxVal: 1, valGridLine: { color: "E6E2F5", size: 0.5 }, catGridLine: { style: "none" },
  });
  s.addText(`Best score model: ${M.best_regressor} (MAE ${reg[M.best_regressor].MAE.toFixed(1)} marks). Best level model: ${M.best_classifier}. Linear regression wins partly because the synthetic score is mostly linear; real data may favour the forest.`,
    { x: 0.5, y: 4.3, w: 9, h: 0.8, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
}

// 11 ----------------------------------------------------------------- classifier results
{
  const s = content("Level prediction results");
  s.addImage({ path: FIG + "08_confusion_matrix.png", x: 0.5, y: 1.15, w: 3.9, h: 3.19 });
  const best = M.classification[M.best_classifier];
  stat(s, 4.9, 1.2, 2.2, `${(best.Accuracy * 100).toFixed(1)}%`, "test accuracy");
  stat(s, 7.2, 1.2, 2.3, best.F1_macro.toFixed(2), "macro F1", GREEN);
  const cm = M.confusion_matrix;
  s.addText(`Mistakes happen between neighbouring levels. No Low student was labelled High and no High student Low (${cm[0][2]} and ${cm[2][0]} cases). Test set: ${M.test_size} students; 5-fold CV accuracy ${best.CV_Accuracy_mean.toFixed(2)}.`,
    { x: 4.9, y: 2.9, w: 4.6, h: 1.6, fontFace: BODY, fontSize: 16, color: INK, margin: 0, valign: "top", isTextBox: true });
}

// 12 ----------------------------------------------------------------- features
{
  const s = content("Key factors affecting performance");
  s.addImage({ path: FIG + "11_feature_importance.png", x: 0.5, y: 1.15, w: 5.2, h: 3.71 });
  const top = Object.entries(M.feature_importance).slice(0, 3);
  s.addText("Top drivers", { x: 6.1, y: 1.2, w: 3.4, h: 0.4, fontFace: HEAD, fontSize: 18, bold: true, color: INDIGO, margin: 0, isTextBox: true });
  top.forEach(([k, v], i) => {
    s.addText(`${(v * 100).toFixed(0)}%`, { x: 6.1, y: 1.75 + i * 0.85, w: 1.3, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: INDIGO, margin: 0, valign: "middle", isTextBox: true });
    s.addText(k.replace("_", " "), { x: 7.4, y: 1.75 + i * 0.85, w: 2.1, h: 0.7, fontFace: BODY, fontSize: 16, color: INK, margin: 0, valign: "middle", isTextBox: true });
  });
  s.addText("Background attributes such as gender or tutoring each add under 1%.", { x: 6.1, y: 4.3, w: 3.4, h: 0.7, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
}

// 13 ----------------------------------------------------------------- dashboard
{
  const s = content("Module 4: Streamlit dashboard");
  const tabs = [["Overview", "KPIs, level mix, factor importance"], ["Predict a student", "Enter details, get score, level, advice"], ["Student comparison", "Compare up to 5 students"],
    ["Subject-wise", "Averages and spread by subject"], ["Performance trends", "Factor vs score, category effects"], ["Recommendations", "Advice for any student"], ["Model details", "Metrics and confusion matrix"]];
  tabs.forEach(([h, d], i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = 0.5 + col * 2.28, y = 1.25 + row * 1.9, w = 2.12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 1.65, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.1 });
    s.addText(h, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: 0.5, fontFace: HEAD, fontSize: 15, bold: true, color: INDIGO, margin: 0, valign: "top", isTextBox: true });
    s.addText(d, { x: x + 0.15, y: y + 0.7, w: w - 0.3, h: 0.85, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("[Insert dashboard screenshots here]", { x: 7.45, y: 3.15, w: 2.0, h: 1.65, fontFace: BODY, fontSize: 14, italic: true, color: RED, margin: 0, valign: "middle", isTextBox: true });
}

// 14 ----------------------------------------------------------------- recommendations
{
  const s = content("Module 5: Recommendation system");
  const ex = M.sample_recommendations;
  const pick = [ex[0], ex[1]];
  pick.forEach((e, i) => {
    const x = 0.5 + i * 4.6, col = e.predicted_level === "Low" ? RED : AMBER;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.2, w: 4.4, h: 3.7, fill: { color: TINT }, line: { color: TINT }, rectRadius: 0.1 });
    s.addText(`${e.student_id}: predicted ${e.predicted_level} (${e.predicted_score.toFixed(0)})`, { x: x + 0.2, y: 1.3, w: 4.0, h: 0.4, fontFace: HEAD, fontSize: 15, bold: true, color: col, margin: 0, isTextBox: true });
    const items = e.recommendations.slice(0, 3).map((r, j, arr) => ({ text: r, options: { bullet: true, breakLine: j < arr.length - 1 } }));
    s.addText(items, { x: x + 0.2, y: 1.8, w: 4.0, h: 3.0, fontFace: BODY, fontSize: 14, color: INK, paraSpaceAfter: 6, margin: 0, valign: "top", isTextBox: true });
  });
}

// 15 ----------------------------------------------------------------- conclusion
{
  const s = pres.addSlide(); n++;
  s.background = { color: INDIGO };
  s.addText("Conclusion", { x: 0.7, y: 0.5, w: 8.6, h: 0.8, fontFace: HEAD, fontSize: 36, bold: true, color: WHITE, margin: 0, isTextBox: true });
  const items = [
    `Complete pipeline: ${M.clean_rows.toLocaleString()} clean records, EDA, models, dashboard, recommendations`,
    `Score predicted within about ${M.regression[M.best_regressor].MAE.toFixed(1)} marks; level predicted with ${(M.classification[M.best_classifier].Accuracy * 100).toFixed(1)}% accuracy`,
    "Internal marks, previous score and study hours matter most",
    "Limits: synthetic data, rule-based advice. Next: real dataset and SHAP explanations",
  ].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } }));
  s.addText(items, { x: 0.7, y: 1.6, w: 8.6, h: 2.6, fontFace: BODY, fontSize: 18, color: "ECE9FC", paraSpaceAfter: 10, margin: 0, valign: "top", isTextBox: true });
  s.addText("Deployment: [paste link]   |   GitHub: [paste link]", { x: 0.7, y: 4.6, w: 8.6, h: 0.4, fontFace: BODY, fontSize: 14, color: "C9C2F5", margin: 0, isTextBox: true });
}

pres.writeFile({ fileName: "Student_Performance_Prediction_Presentation.pptx" }).then(() => console.log("saved"));
