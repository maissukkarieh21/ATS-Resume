from flask import Flask, request, jsonify
from ats_checker import is_ats_friendly  # Import your ATS checking function

app = Flask(__name__)

@app.route('/check_ats', methods=['POST'])
def check_ats_compliance():
    # Get the uploaded CV file and job description from the form
    cv_file = request.files.get('cvFile')
    if not cv_file:
        return jsonify({'error': 'CV file is required'}), 400

    job_description = request.form.get('jobDescription')
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    # Save the CV file temporarily
    cv_file_path = f"temp_{cv_file.filename}"
    cv_file.save(cv_file_path)

    # Call your ATS checking function (implement it in ats_checker.py)
    result = is_ats_friendly(cv_file_path, job_description)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)