
import logging
import json
from flask import Flask, request,render_template, jsonify
from datetime import datetime, timedelta
from db.utiles import add_to_db, read_table
from db.db_agent import DBAgent

app = Flask(__name__, template_folder='../web')
# Set up logging configuration to capture debug level messages
logging.basicConfig(
    filename='app.log',  # The log file where messages will be stored
    level=logging.DEBUG,  # Capture messages of DEBUG level and higher
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
ROLES = [
    "Sunday School Teacher",
    "Assistant",
    "Chinese Sunday School leader",
    "Youth fellowship leader",
    "Piano",
    "Others"
]

PEOPLE = [
    "Lilian", "Sarah", "Annie", "Jeremy", "Andrea", "Emma", "Selina", "Faith",
    "Abby", "Aslan", "Ethan", "Abel", "Jessica", "Rachel", "Rae-Anne", "Arielle", "Yu-Ang"
]
@app.route('/')
def home():
    return render_template('volunteer.html')

@app.route('/report', methods=['GET'])
def report():
    # Get the selected name from the query parameters
    selected_name = request.args.get('name')

    # If no name is selected, show an empty table
    if not selected_name:
        return render_template('report.html', results=None, selected_name=None)

    # Define the query for fetching data
    query = """
    SELECT sunday_date, JSON_UNQUOTE(JSON_SEARCH(json_data, 'one', %s)) AS role
    FROM Sundays2025
    WHERE JSON_SEARCH(json_data, 'one', %s) IS NOT NULL;
    """

    try:
        # Initialize the database agent and execute the query
        db_agent = DBAgent()
        results = db_agent.execute_query(query, (selected_name, selected_name))
    except Exception as e:
        # Log the error and render an error page (or handle it as needed)
        print(f"Database error: {e}")
        return render_template('error.html', error_message="An error occurred while processing your request.")

    # Render the results
    return render_template('report.html', results=results, selected_name=selected_name)

@app.route('/volunteer')

def volunteer():
    return render_template('volunteer.html')
'''
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    try:
        # Query to get upcoming dates
        query = "select sunday_date from Sundays2025 where sunday_date >= CURDATE()"
     #   query = "select sunday_date from Sundays2025"
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
        '''
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
      if request.method == 'POST':
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Validate that dates are not empty
        if not start_date or not end_date:
            return "Error: Missing start_date or end_date", 400

        try:
            # Convert strings to datetime objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            return f"Error: Invalid date format. Expected YYYY-MM-DD. Error: {e}", 400

        # Generate list of dates in range with roles and assigned names
        dates_in_range = []
        current_date = start_date
        while current_date <= end_date:
            header_name = current_date.strftime('%A, %Y-%m-%d')  # Example: "Sunday, 2023-10-01"

            # Generate roles and assigned names for the current date (replace with your logic)
            roles = []
            for role in ROLES:
                # Example: Assign a random person to each role (replace with your logic)
                assigned_person = PEOPLE[(ROLES.index(role) + current_date.day) % len(PEOPLE)]
                roles.append({
                    'name': role,
                    'assigned_person': assigned_person  # Pass the assigned person from the backend
                })

            dates_in_range.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'header_name': header_name,
                'roles': roles
            })
            current_date += timedelta(days=1)

        return render_template('schedule.html', start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'), dates_in_range=dates_in_range, people=PEOPLE)

    # Initial state: No dates selected
        return render_template('schedule.html', start_date=None, end_date=None, dates_in_range=None, people=PEOPLE)

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
    # Define the expected order of roles
    expected_roles = ["Sunday School Teacher", "Assistant", "Chinese Sunday School leader", "Youth fellowship leader", "Piano", "Others"]  # Replace with your actual role keys

    selected_date = request.form.get("date")

    # Build selected_roles with the expected order
    selected_roles = {
        role: request.form.get(role, None)  # Use None or a default value if the role isn't in the form
        for role in expected_roles
    }

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