import mysql.connector  # For MySQL

# Configure your database connection
mydb = mysql.connector.connect(
    host= "joycelin53.mysql.pythonanywhere-services.com",       # Replace with your database host
    user= "joycelin53",       # Replace with your database username
    password= "Dbaccess",  # Replace with your database password
    database= "joycelin53$default"  # Replace with your database name
)
mycursor=mydb.cursor()

mycursor.execute("SELECT * FROM attendance")
myresult=mycursor.fetchall()

for x in myresult:
    print(x)
