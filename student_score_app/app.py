from flask import Flask, render_template, request, jsonify, Response, send_file
import os
import io
import csv
import pandas as pd
try:
    from ml_engine import StudentScoreMLEngine
except ImportError:
    from student_score_app.ml_engine import StudentScoreMLEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-score-ai-secret-key-2025'

# Initialize ML Engine
ml_engine = StudentScoreMLEngine()

@app.route("/", methods=["GET"])
def index():
    initial_inputs = {
        'hours': 6.0,
        'sleep': 7.0,
        'attendance': 85.0,
        'assignments': 6.0,
        'model': 'ensemble'
    }
    initial_prediction = ml_engine.predict(
        hours=initial_inputs['hours'],
        sleep=initial_inputs['sleep'],
        attendance=initial_inputs['attendance'],
        assignments=initial_inputs['assignments'],
        model_name=initial_inputs['model']
    )
    metrics_summary = ml_engine.get_metrics_summary()
    dataset_info = ml_engine.get_dataset_records(limit=25)

    return render_template(
        "index.html",
        initial_prediction=initial_prediction,
        inputs=initial_inputs,
        metrics=metrics_summary,
        dataset=dataset_info
    )

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if request.is_json:
            data = request.get_json()
            hours = float(data.get("hours", 6.0))
            sleep = float(data.get("sleep", 7.0))
            attendance = float(data.get("attendance", 85.0))
            assignments = float(data.get("assignments", 6.0))
            model_name = data.get("model", "ensemble")
        else:
            hours = float(request.form.get("hours", 6.0))
            sleep = float(request.form.get("sleep", 7.0))
            attendance = float(request.form.get("attendance", 85.0))
            assignments = float(request.form.get("assignments", 6.0))
            model_name = request.form.get("model", "ensemble")

        result = ml_engine.predict(hours, sleep, attendance, assignments, model_name=model_name)

        # If AJAX / JSON request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json or "application/json" in request.headers.get("Accept", ""):
            return jsonify(result)

        # Traditional form fallback
        return render_template(
            "result.html",
            prediction=result['score'],
            result=result,
            inputs=result['inputs'],
            metrics=ml_engine.get_metrics_summary()
        )
    except Exception as e:
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": str(e)}), 400
        return f"Error processing prediction: {e}", 400

@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json(force=True)
        hours = float(data.get("hours", 6.0))
        sleep = float(data.get("sleep", 7.0))
        attendance = float(data.get("attendance", 85.0))
        assignments = float(data.get("assignments", 6.0))
        model_name = data.get("model", "ensemble")

        result = ml_engine.predict(hours, sleep, attendance, assignments, model_name=model_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/optimize", methods=["POST"])
def api_optimize():
    try:
        data = request.get_json(force=True)
        target_score = float(data.get("target_score", 85.0))
        sleep = float(data.get("sleep", 7.0))
        attendance = float(data.get("attendance", 85.0))
        assignments = float(data.get("assignments", 7.0))

        plan = ml_engine.optimize_for_target(
            target_score=target_score,
            current_sleep=sleep,
            current_attendance=attendance,
            current_assignments=assignments
        )
        return jsonify(plan)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/batch-predict", methods=["POST"])
def api_batch_predict():
    try:
        model_name = request.form.get("model", "ensemble")
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Unsupported file format. Please upload CSV or Excel (.xlsx)."}), 400

        batch_results_df = ml_engine.batch_predict(df, model_name=model_name)
        records = batch_results_df.to_dict(orient="records")

        # Compute summary stats
        avg_score = round(float(batch_results_df['Predicted_Score'].mean()), 2)
        pass_rate = round(float((batch_results_df['Predicted_Score'] >= 50).mean() * 100), 1)
        grade_dist = batch_results_df['Grade'].value_counts().to_dict()

        return jsonify({
            'records': records,
            'summary': {
                'total_students': len(records),
                'avg_score': avg_score,
                'pass_rate': pass_rate,
                'grade_distribution': grade_dist
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/download-template", methods=["GET"])
def download_template():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student_Name', 'Hours', 'Sleep', 'Attendance', 'Assignments'])
    writer.writerow(['Alex Morgan', 8.5, 7.0, 95.0, 8])
    writer.writerow(['Samantha Lee', 4.5, 6.0, 80.0, 5])
    writer.writerow(['Marcus Chen', 10.0, 7.5, 98.0, 9])
    writer.writerow(['David Miller', 3.0, 5.0, 65.0, 3])
    writer.writerow(['Elena Rostova', 6.5, 8.0, 88.0, 7])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=student_batch_template.csv"}
    )

@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    return jsonify(ml_engine.get_metrics_summary())

@app.route("/data", methods=["GET"])
def data():
    csv_path = os.path.join(os.path.dirname(__file__), "student_performance.csv")
    xlsx_path = os.path.join(os.path.dirname(__file__), "student_performance.xlsx")

    df = None
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(xlsx_path):
        df = pd.read_excel(xlsx_path)

    if df is not None:
        if request.args.get("format") == "json":
            return jsonify(df.to_dict(orient="records"))
        return df.to_html(classes='table table-striped table-hover', index=False)
    return "Dataset preview not available."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7860)
