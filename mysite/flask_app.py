
import logging
import json
from flask import Flask, request,render_template, jsonify
from datetime import datetime
from db.utiles import add_to_db, read_table
from db.db_agent import DBAgent
from collections import OrderedDict

app = Flask(__name__, template_folder='../web')
# Set up logging configuration to capture debug level messages
logging.basicConfig(
    filename='app.log',  # The log file where messages will be stored
    level=logging.DEBUG,  # Capture messages of DEBUG level and higher
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

@app.route('/')
def home():
    return render_template('volunteer.html')
@app.route('/volunteer')

def volunteer():
    return render_template('volunteer.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    try:
        # Query to get upcoming dates
     #   query = "select sunday_date from Sundays2025 where sunday_date >= CURDATE()"
        query = "select sunday_date from Sundays2025"
        db_agent = DBAgent()
        results = db_agent.execute_query(query)
        dates = [str(row[0]) for row in results]

        # If no date is selected, set the first date as default
        if request.method == 'POST':
            selected_date = request.form.get('date')
        else:
            selected_date = dates[0] if dates else None  # Default to the first date

        # Handle roles loading based on selected date
        roles = load_roles(selected_date)

        # Render the schedule template with the roles and available dates
        return render_template("schedule.html", dates=dates, selected_date=selected_date, roles=roles)

    except Exception as e:
        logging.error("Unexpected error: %s", e)
        return "An unexpected error occurred. Please check the logs for details.", 500

@app.route('/view', methods=['GET', 'POST'])
def view_schedule():
    try:
        # Example context data
        query = "select sunday_date from Sundays2025 where sunday_date <= CURDATE()"
        db_agent = DBAgent()
        results = db_agent.execute_query(query)
        dates = [str(row[0]) for row in results] # Example dates
        if request.method == 'POST':
            selected_date = request.form.get('date')
        else:
            selected_date = dates[0] if dates else None
        roles = load_roles(selected_date)
        logging.debug(f"Selected date: {selected_date}")
        logging.debug(f"Roles: {roles}")

        # Render the HTML template with context
        return render_template(
            "view.html",  # Update this to match your template filename
            selected_date=selected_date,
            dates=dates,
            roles=roles
        )

    except Exception as e:
        logging.error(f"Error in view_schedule: {e}")
        return "An error occurred while rendering the schedule.", 500



@app.route('/attendance-check', methods=['GET','POST'])
def attendance_check():
    app.logger.debug("Data fetched for attendance check start...")
    query = "SELECT DISTINCT attendance_date FROM attendance"
    db_agent = DBAgent()
    results = db_agent.execute_query(query)
    years = [str(row[0]) for row in results]
    selected_year = None
    if request.method == 'POST':
        # Get the selected year from the form
        selected_year = request.form.get('year')
        if selected_year:
            query = """
            SELECT A.id, M.FullName, A.attendance_date
            FROM attendance A
            JOIN Members M ON A.Member_id = M.Member_id
            WHERE A.attendance_date = %s
            """
    # Get the selected year (default to 2025 if not provided)
    attendance_data = db_agent.execute_query(query, (selected_year,))
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

@app.route('/submit', methods=['POST'])
def submit():
    selected_date = request.form.get("date")

    # Get selected names for each role (whether selected from dropdown or typed in)
    selected_roles = OrderedDict((role, request.form.get(role)) for role in request.form if role != "date")

    # Convert roles to JSON format for storing in the database
    json_data = json.dumps(selected_roles)

    # Update the database with the selected roles
    query = "UPDATE Sundays2025 SET json_data=%s WHERE sunday_date=%s"
    db_agent = DBAgent()
    params = (json_data, selected_date)
    db_agent.execute_update(query, params)

    return jsonify({
        "date": selected_date,
        "roles": selected_roles
    })

@app.route('/test', methods=['GET'])
def display_record():
    query = "SELECT id, Member_id, attendance_date FROM attendance"
    attendance_data = read_table(query)
    return f'Attendance created for {attendance_data}'

def load_roles(selected_date, json_file_path="leader.json"):
    """
    Load roles either from the database or from a JSON file.

    Args:
        selected_date (str): The date to query in the database.
        json_file_path (str): Path to the fallback JSON file.

    Returns:
        dict: Loaded roles as a dictionary.
    """
    if not selected_date:
        return {}
    query = "SELECT json_data FROM Sundays2025 WHERE sunday_date = %s"
    try:
        # Try to fetch data from the database
        db_agent = DBAgent()
        result = db_agent.execute_query(query, (selected_date,))

        if result and result[0][0]:  # Check if a result is returned and the json_data field is not null
            json_data = result[0][0]
            roles = json.loads(json_data)  # Parse JSON data from the database
            #print("Loaded roles from the database:", roles)
        else:
           # roles = None
            # Fallback: Load roles from the JSON file
            with open(json_file_path, 'r') as file:
                roles = json.load(file)
            #print("Loaded roles from the JSON file:", roles)

        return roles

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading roles: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True)