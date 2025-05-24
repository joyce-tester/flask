from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
from db.db_agent import DBAgent  # Import the DBAgent class
import json

app = Flask(__name__, template_folder='../web')

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
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            return "Error: Missing start_date or end_date", 400

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            return f"Error: Invalid date format. Expected YYYY-MM-DD. Error: {e}", 400

        # Query the database for Sundays2025 data within the selected date range
        query = """
        SELECT sunday_date, json_data
        FROM Sundays2025
        WHERE sunday_date BETWEEN %s AND %s
        """
        db_agent = DBAgent()
        results = db_agent.execute_query(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        dates_in_range = []
        for row in results:
            sunday_date = row[0]  # First column is sunday_date
            json_data = row[1]  # Second column is json_data (may be None)

            # If json_data is None, initialize an empty dictionary
            if json_data is None:
                json_data = {}
            else:
                json_data = json.loads(json_data)  # Parse JSON data

            # Generate roles and assigned names for the current date
            roles = []
            for role in ROLES:
                assigned_person = json_data.get(role, "")  # Get the assigned person for the role (default to empty string)
                roles.append({
                    'name': role,
                    'assigned_person': assigned_person
                })

            dates_in_range.append({
                'date': sunday_date.strftime('%Y-%m-%d'),
                'header_name': sunday_date.strftime('%A, %Y-%m-%d'),
                'roles': roles
            })

        return render_template('schedule.html', start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'), dates_in_range=dates_in_range, people=PEOPLE)

    return render_template('schedule.html', start_date=None, end_date=None, dates_in_range=None, people=PEOPLE)

@app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form
    selected_roles = {}

    for key, value in form_data.items():
        if key.startswith(tuple(ROLES)):
            role, date = key.rsplit('_', 1)
            if date not in selected_roles:
                selected_roles[date] = {}
            selected_roles[date][role] = value

    # Update the database with the selected roles
    db_agent = DBAgent()
    for date, roles in selected_roles.items():
        json_data = json.dumps(roles)
        query = """
        UPDATE Sundays2025
        SET json_data = %s
        WHERE sunday_date = %s
        """
        db_agent.execute_update(query, (json_data, date))

    return jsonify({
        "message": "Schedule submitted successfully!",
        "selected_roles": selected_roles
    })
@app.route('/materials')
def materials():
    # Load retreat materials
    try:
        with open('retreat_materials.json', 'r') as file:
            retreat_materials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        retreat_materials = []

    # Load learning materials
    try:
        with open('learning_materials.json', 'r') as file:
            learning_materials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        learning_materials = []

    # Optionally load sunday school materials
    sunday_materials = []  # Placeholder

    return render_template(
        'materials.html',
        retreat_materials=retreat_materials,
        learning_materials=learning_materials,
        sunday_materials=sunday_materials
    )
@app.route('/learning-materials')
def learning_materials():
    # Load learning materials from a JSON file
    try:
        with open('learning_materials.json', 'r') as file:
            learning_materials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        learning_materials = []  # Default to an empty list if the file is missing or corrupted

    return render_template('learning_materials.html', learning_materials=learning_materials)
@app.route('/retreat-materials')
def retreat_materials():
    # Load learning materials from a JSON file
    try:
        with open('retreat_materials.json', 'r') as file:
            retreat_materials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        retreat_materials = []  # Default to an empty list if the file is missing or corrupted

    return render_template('retreat_materials.html', retreat_materials=retreat_materials)
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

        # Render the HTML template with context
        return render_template(
            "view.html",  # Update this to match your template filename
            selected_date=selected_date,
            dates=dates,
            roles=roles
        )

    except Exception as e:
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


def load_roles(selected_date, json_file_path="leader.json"):

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
    app.run(debug=True)