
import logging
from flask import Flask, request,render_template, jsonify
from datetime import datetime
from db.utiles import add_to_db, read_table


app = Flask(__name__, template_folder='../web')
# Set up logging configuration to capture debug level messages
logging.basicConfig(
    filename='app.log',  # The log file where messages will be stored
    level=logging.DEBUG,  # Capture messages of DEBUG level and higher
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

@app.route('/')
def home():
    return render_template('schedule.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/attendance-check', methods=['GET','POST'])
def attendance_check():
    app.logger.debug("Data fetched for attendance check start...")
    query = "SELECT DISTINCT attendance_date FROM attendance"
    results = read_table(query)
    years = [str(row[0]) for row in results]
    selected_year = None
    query = "SELECT A.id, M.Member_id, A.attendance_date FROM attendance A join Members M on A.Member_id=M.Member_id"
    if request.method == 'POST':
        # Get the selected year from the form
        selected_year = request.form.get('year')
        if selected_year:
            query = """
            SELECT A.id, M.Member_id, A.attendance_date
            FROM attendance A
            JOIN Members M ON A.Member_id = M.Member_id
            WHERE strftime('%Y', A.attendance_date) = ?
            """
    # Get the selected year (default to 2025 if not provided)
  #  selected_year = int(request.form.get('year', 2025))
  #  query = "SELECT A.id, M.Member_id, A.attendance_date FROM attendance A join Members M on A.Member_id=M.Member_id"
    attendance_data = read_table(query)
    app.logger.debug("Data fetched for attendance check: %s", attendance_data)
    return render_template(
        'attendance_check.html',
        years=years,
        selected_year=selected_year,
        data=attendance_data
    )


@app.route('/add', methods=['GET'])
def add_attendance():
    # Example usage of addtoDB function
    id = request.args.get('id', 'Unknown')
    attendance_date = datetime.now().strftime("%Y-%m-%d")

    if not id or not attendance_date:
        return jsonify({"error": "Missing member_id or attendance_date"}), 400

    try:
        add_to_db(id, attendance_date)
        return jsonify({"message": "Record added successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/test', methods=['GET'])
def display_record():
    query = "SELECT id, Member_id, attendance_date FROM attendance"
    attendance_data = read_table(query)
    return f'Attendance created for {attendance_data}'


if __name__ == '__main__':
    app.run(debug=True)