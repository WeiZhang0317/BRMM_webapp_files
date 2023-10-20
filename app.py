from flask import Flask, render_template, request, redirect, url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

connection = None

def getCursor(dictionary_cursor=False):
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, database=connect.dbname, autocommit=True)
    cursor = connection.cursor(dictionary=dictionary_cursor)
    return cursor

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/admin_interface")
def admin_interface():
    return render_template("admin_interface.html")

#----------------------------------------------------------------


@app.route("/listdrivers")
def listdrivers():
    cursor = getCursor()
    sql_query = """
    SELECT
        driver.driver_id AS driver_id,
        driver.age AS age,
        CONCAT(driver.first_name, ' ', driver.surname) AS driver_name,
        car.model AS car_model,
        car.drive_class AS drive_class
    FROM
        driver
    JOIN
        car ON driver.car = car.car_num
    ORDER BY 
        driver.surname, driver.first_name;    
    """
    cursor.execute(sql_query)
    driver_details = cursor.fetchall()
    connection.close()
    return render_template("listdrivers.html", drivers=driver_details)




@app.route("/driverdetails", methods=["GET", "POST"])
def driverdetails():
    # Retrieving the driver's name from the URL query parameters, if available.
    driver_name_from_url = request.args.get('driver_name') 
    # Establishing a connection to the database and creating a cursor object with dictionary support.
    cursor = getCursor(dictionary_cursor=True)

    # Check if the request is a POST request or if there's a driver name in the URL.
    if request.method == "POST" or driver_name_from_url:
        # If the "return" button was pressed on the form, we fetch the names again and display the initial form.
        if request.form.get("return"):
            # Executing a SQL command to get all driver names.
            cursor.execute("SELECT CONCAT(first_name, ' ', surname) AS driver_name FROM driver;")
            # Storing the list of driver names.
            driver_names = [row['driver_name'] for row in cursor.fetchall()]
            # Closing the database connection.
            connection.close()
            # Returning the HTML page with a list of driver names.
            return render_template("driverdetails.html", driver_names=driver_names)
        else:
            # If there's a driver name in the URL, use it; otherwise, get the driver's name from the posted form.
            selected_driver = driver_name_from_url if driver_name_from_url else request.form.get("driver_name")
            
            # SQL query to gather detailed information about the selected driver, including performance stats.
            sql_query = """
            SELECT
                driver.driver_id AS driver_id,
                CONCAT(driver.first_name, ' ', driver.surname) AS driver_name,
                course.name AS course_name,
                run.run_num AS run_number,
                run.seconds AS seconds,
                IFNULL(run.cones, 0) AS cones,
                run.wd AS wd,
                ROUND((run.seconds + IFNULL(run.cones, 0) * 5 + run.wd * 10), 2) AS run_total,  -- Calculating total score with penalties, rounded to two decimal places.
                car.model AS car_model,
                car.drive_class AS drive_class
            FROM
                driver
            JOIN
                run ON driver.driver_id = run.dr_id
            JOIN
                course ON run.crs_id = course.course_id
            JOIN
                car ON driver.car = car.car_num
            WHERE CONCAT(driver.first_name, ' ', driver.surname) = %s;
            """
            # Executing the SQL query with the selected driver's name.
            cursor.execute(sql_query, (selected_driver,))
            # Retrieving all the details of the selected driver.
            driver_details = cursor.fetchall()
            # Closing the database connection.
            connection.close()
            # Returning the HTML page with detailed information about the selected driver.
            return render_template("driverdetails.html", driver_list=driver_details, selected_driver=selected_driver)

    # If it's a GET request without a driver name in the URL, we prepare the initial form with all driver names.
    cursor.execute("SELECT CONCAT(first_name, ' ', surname) AS driver_name FROM driver;")
    # Storing the list of driver names.
    driver_names = [row['driver_name'] for row in cursor.fetchall()]
    # Closing the database connection.
    connection.close()
    # Returning the HTML page with a list of driver names for initial selection.
    return render_template("driverdetails.html", driver_names=driver_names)


def fetch_overallresults():
    cursor = getCursor()
    sql_query="""
    with base as 
    (
    SELECT
                    driver.driver_id AS driver_id,
                    CONCAT(driver.first_name, ' ',
                    case when age is not null then concat(driver.surname,'(J)') else  driver.surname  end
                    ) AS driver_name,
                    course.name AS course_name,
                    run.run_num AS run_number,
                    run.seconds AS seconds,
                    IFNULL(run.cones, 0) AS cones,
                    run.wd AS wd,
                    ROUND((run.seconds + IFNULL(run.cones, 0) * 5 + run.wd * 10), 2) AS run_total,  
                    car.model AS car_model,
                    car.drive_class AS drive_class
                FROM
                    driver
                JOIN
                    run ON driver.driver_id = run.dr_id
                JOIN
                    course ON run.crs_id = course.course_id
                JOIN
                    car ON driver.car = car.car_num
        ),
        fast_one as (
        select  driver_id,driver_name,course_name,car_model,
        case when  min(seconds) is null then 'dnf' else  round(min(seconds),2) end as course_time
        from base 
        group by driver_id,driver_name,course_name,car_model
        ),
        to_columns as (
        select 
        driver_id,driver_name,car_model,
        max(case when course_name='Going Loopy' then course_time else null end) as GoingLoopy,
        max(case when course_name='Walnut' then course_time else null end) as Walnut,
        max(case when course_name='Shoulders Back' then course_time else null end) as ShouldersBack,
        max(case when course_name="Mum's Favourite" then course_time else null end) as Mum_Favourite,
        max(case when course_name='Hamburger' then course_time else null end) as Hamburger,
        max(case when course_name='Cracked Fluorescent' then course_time else null end) as CrackedFluorescent
        from 
        fast_one
        group by driver_id,driver_name,car_model
        ),
        to_overall as (
        select   driver_id, driver_name, car_model, 
        GoingLoopy,Walnut,ShouldersBack,Mum_Favourite,Hamburger,CrackedFluorescent,
        case when GoingLoopy='dnf' or Walnut='dnf' or ShouldersBack='dnf' or Mum_Favourite='dnf' or Hamburger='dnf' or CrackedFluorescent='dnf'
        then 'NotQualified'
        else round(GoingLoopy+Walnut+ShouldersBack+Mum_Favourite+Hamburger+CrackedFluorescent,2) end as OverallResult
        from to_columns
        ),
        to_rank as (
        select *, dense_rank() over ( order by case when overallresult='NotQualified' then 99999999 else overallresult end asc) as ranks from to_overall
        ),
        to_prize as (
        select *,
        case when ranks between 2 and 5 then 'prize' when ranks=1 then 'cup' else null end as prize 
        from to_rank
        )
        select driver_id, driver_name, car_model, GoingLoopy, Mum_Favourite,Walnut, Hamburger, ShouldersBack,  CrackedFluorescent, OverallResult, prize 
        from to_prize
        order by ranks 
        """
    cursor.execute(sql_query)
    overallResults=cursor.fetchall()
    return overallResults



@app.route("/overallresults")
def overallresults():
    overallResults=fetch_overallresults()
    return render_template("overallresults.html",results=overallResults)   




@app.route("/listcourses")
#decorator, the address user is going to visit
#List of courses: Make the courselist page display the course’s image, rather than the name of 
#the image file. Modify or tidy the template as appropriate.
def listcourses():
    connection = getCursor()
    #connect with database
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    #select all the information from course in database  
    #return back to courselist (a list of tuple)
    #which is [(courseid,coursename, course_images),...]
    return render_template("courselist.html", course_list = courseList)


@app.route("/graph")
def showgraph():
    overallResults=fetch_overallresults()

    # Extract the names of the top 5 drivers from the overall results.
    bestDriverList = [result[1] for result in overallResults[0:5]]
    # Extract the scores/results associated with the top 5 drivers.  
    resultsList = [result[9] for result in overallResults[0:5]]
    # Render the graph template and pass in the names and scores of the top drivers.
    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)


@app.route("/juniordriverlist")
def juniordriverlist():
    cursor=getCursor()
    sql_query="""
    SELECT 
    driver_id, 
    CONCAT(driver.first_name, ' ', driver.surname) AS driver_name,
    driver.date_of_birth, 
    driver.age, 
    driver.caregiver
    FROM driver
    order by driver.age desc, driver.surname
"""
    cursor.execute(sql_query)
    driverlist=cursor.fetchall()
    
    finallist=[]

    for listoftp in driverlist:
        listofli=list(listoftp)
        caregiverid=listofli[4]

 #replace the caregiverid to the caregiver name                       
        if caregiverid is not None:
            for inner_listoftp in driverlist:
                if inner_listoftp[0]==caregiverid:
                    caregivername=inner_listoftp[1]
                    listofli[4]=caregivername
                    break
#find the age is not none and put it to junior list
        if listofli[3] is not None:
           finallist.append(listofli)       

    return render_template("juniordriverlist.html", juniorlist=finallist)

@app.route("/searchname", methods=["GET", "POST"])
def searchname():
   drivers=[]
   if request.method == "POST":
      keyword = f"%{request.form['keyword']}%"
      cursor=getCursor()
      sql_query="""SELECT CONCAT(driver.first_name, ' ', driver.surname) AS driver_name
FROM driver WHERE driver.first_name LIKE %s OR driver.surname LIKE %s"""
      cursor.execute(sql_query, (keyword,keyword))
      drivers=cursor.fetchall()
   return render_template("searchname.html", drivername=drivers)



@app.route("/edit_runs")
def edit_runs():
    return render_template("edit_runs.html")




@app.route("/edit_runs_driver", methods=["GET", "POST"])
def edit_runs_driver():
    # Get a cursor from the database connection. This cursor returns results as a dictionary.
    cursor = getCursor(dictionary_cursor=True)

    # If the request method is GET, retrieve and display all drivers' names.
    cursor.execute("SELECT CONCAT(first_name, ' ', surname) AS driver_name FROM driver;")
    driver_names = [row['driver_name'] for row in cursor.fetchall()]

    # If the request method is POST, several actions are possible based on the submitted form data.
    if request.method == "POST":

        # If the 'return' button was pressed, redirect to the same page.
        if request.form.get("return"):
            return redirect(url_for('edit_runs_driver'))

        # If the 'edit' button was pressed, update the driver's run data based on the form inputs.
        elif request.form.get("edit") == "true":  
            # Iterate through the form's key-value pairs.
            for driver in request.form:
                # Check if the current form input's name indicates it's related to run data.
                if any(prefix in driver for prefix in ['seconds_', 'cones_', 'wd_']):
                    # Extract details from the form input's name.
                    parts = driver.split("_")  # Split the string at underscores.
                    column = parts[0]  # E.g., "seconds"
                    driver_id = parts[1]
                    course_id = parts[2]
                    run_number = parts[3]
                    value = request.form[driver]  # Get the input's value from the form.

                    # If the form input is empty, prepare to insert a NULL value into the database.
                    if value == "":
                        value = None  

                    # Prepare and execute the SQL update statement.
                    update_query = f"UPDATE run SET {column} = %s WHERE dr_id = %s AND crs_id=%s AND run_num=%s"
                    cursor.execute(update_query, (value, driver_id, course_id, run_number))

            # Commit the updates to the database.
            connection.commit()
            # Redirect to refresh the page with updated data.
            return redirect(url_for('edit_runs_driver'))

        # If a driver was selected from the list, retrieve and display that driver's detailed information.
        else:
            selected_driver = request.form.get("driver_name")
            # SQL query to retrieve detailed information for the selected driver.
            sql_query = """
                SELECT
                    driver.driver_id AS driver_id,
                    CONCAT(driver.first_name, ' ', driver.surname) AS driver_name,
                    run.crs_id AS course_id,
                    course.name AS course_name,
                    run.run_num AS run_number,
                    run.seconds AS seconds,
                    IFNULL(run.cones, 0) AS cones,
                    run.wd AS wd
                FROM
                    driver
                JOIN
                    run ON driver.driver_id = run.dr_id
                JOIN
                    course ON run.crs_id = course.course_id
                WHERE CONCAT(driver.first_name, ' ', driver.surname) = %s;
            """
            cursor.execute(sql_query, (selected_driver,))
            driver_details = cursor.fetchall()
            return render_template("edit_runs_driver.html", driver_list=driver_details, selected_driver=selected_driver)

    # Close the database connection.
    connection.close()  

    # For a GET request, render the template with the list of drivers' names.
    return render_template("edit_runs_driver.html", driver_names=driver_names)


@app.route("/edit_runs_course", methods=["GET", "POST"])
def edit_runs_course():
    # Establish a new connection and create a new cursor from the database connection. The cursor returns results as a dictionary.
    cursor = getCursor(dictionary_cursor=True)

    # For a GET request, we retrieve and display all course names from the database.
    cursor.execute("SELECT course.name AS course_name FROM course;")
    course_names = [row['course_name'] for row in cursor.fetchall()]

    # Handling the POST request method, which allows data to be sent to the server to be processed.
    if request.method == "POST":

        # If the 'return' button was pressed, it will redirect the user back to the current page.
        if request.form.get("return"):
            return redirect(url_for('edit_runs_course'))

        # If the 'edit' button was pressed, the system updates the respective run's data based on the inputs from the form.
        elif request.form.get("edit") == "true":
            # Loop through each key-value pair in the form data.
            for course in request.form:
                # Check if the current form input's name signifies it holds run data.
                if any(prefix in course for prefix in ['seconds_', 'cones_', 'wd_']):
                    # Extract details from the form input's name.
                    parts = course.split("_")  # Splitting the input name at underscores.
                    column = parts[0]  # E.g., "seconds"
                    driver_id = parts[1]
                    course_id = parts[2]
                    run_number = parts[3]
                    value = request.form[course]  # Getting the actual value for the current input.

                    # If the input value is an empty string, we prepare to insert a NULL value in the database.
                    if value == "":
                        value = None 

                    # Constructing the SQL query for updating the information.
                    update_query = f"UPDATE run SET {column} = %s WHERE dr_id = %s AND crs_id = %s AND run_num = %s"

                    # Executing the update query with the corresponding values.
                    cursor.execute(update_query, (value, driver_id, course_id, run_number))

            # After the loop, we commit all changes to the database.
            connection.commit()

            # Redirect back to refresh the page with the updated information.
            return redirect(url_for('edit_runs_course'))

        # If a specific course was selected from the list, we display detailed information about the runs associated with this course.
        else:
            selected_course = request.form.get("course_name")
            # Constructing the SQL query to retrieve detailed information for the runs related to the selected course.
            sql_query = """
                SELECT
                    driver.driver_id AS driver_id,
                    CONCAT(driver.first_name, ' ', driver.surname) AS driver_name,
                    run.crs_id AS course_id,
                    course.name AS course_name,
                    run.run_num AS run_number,
                    run.seconds AS seconds,
                    IFNULL(run.cones, 0) AS cones,
                    run.wd AS wd
                
                FROM
                    driver
                JOIN
                    run ON driver.driver_id = run.dr_id
                JOIN
                    course ON run.crs_id = course.course_id

                WHERE course.name = %s;
            """
            # Executing the SQL query with the selected course name.
            cursor.execute(sql_query, (selected_course,))
            course_details = cursor.fetchall()

            # Rendering the template with the list of runs for the selected course.
            return render_template("edit_runs_course.html", course_list=course_details, selected_course=selected_course)

    # Close the database connection to free up resources. This is important to prevent data leaks.
    connection.close()  # Ensure that the connection is closed on all paths

    # For a GET request, the system renders the template with the list of course names.
    return render_template("edit_runs_course.html", course_names=course_names)



@app.route("/add_driver")
def add_driver():
    return render_template("add_driver.html")


@app.route("/add_driver_adult", methods=["GET", "POST"])
def add_driver_adult():
    cursor = getCursor(dictionary_cursor=True)
    car_info = []
    
    # This function fetches car information.
    def fetch_car_info():
        cursor.execute("""
            SELECT car.car_num AS car_num,
                   car.model AS car_model
            FROM car ;
        """)
        car_rows = cursor.fetchall()
        for row in car_rows:
            car_info.append(str(row['car_num']) + ' ' + row['car_model'])
    
    # For a GET request, we fetch the car info and render the template.
    if request.method == "GET":
        fetch_car_info()
        return render_template("add_driver_adult.html", existing_cars=car_info)

    # For a POST request, we first handle the form submission by inserting the new driver.
    elif request.method == "POST":
        driver_firstname = request.form['driver_firstname']
        driver_surname = request.form['driver_surname']
        driver_id = request.form['driver_id']
        car_num = request.form['car_model'].split(' ')[0]  # Getting car number
        
        # Insert the new driver
        cursor.execute("""
            INSERT INTO driver (driver_id, first_name, surname, car)
            VALUES (%s, %s, %s, %s)
        """, (driver_id, driver_firstname, driver_surname, car_num))
       
       #update the run table
        crs_ids = ['A', 'B', 'C', 'D', 'E', 'F']
        for crs_id in crs_ids:
            for run_num in [1, 2]:
                cursor.execute("""
                    INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd)
                    VALUES (%s, %s, %s, NULL, NULL, 0)
                """, (driver_id, crs_id, run_num))
        
        # Important: Fetch the car info again before rendering the template.
        fetch_car_info()
        return render_template("add_driver_adult.html", existing_cars=car_info, message="Driver added successfully!")

@app.route("/add_driver_junior", methods=["GET", "POST"])
def add_driver_junior():
    cursor = getCursor(dictionary_cursor=True)

    # This function fetches car information.
    car_info = []   
    def fetch_car_info():
        cursor.execute("""
            SELECT car.car_num AS car_num,
                   car.model AS car_model
            FROM car ;
        """)
        car_rows = cursor.fetchall()
        for row in car_rows:
            car_info.append(str(row['car_num']) + ' ' + row['car_model'])

    # This function fetches caregiver information.
    caregiver_info=[]
    def fetch_caregiver_info():
        cursor.execute("""SELECT CONCAT(driver.driver_id,' ',driver.first_name, ' ', driver.surname) AS caregiver_info FROM driver
        where age is null """)
        caregiver_rows= cursor.fetchall()     
        for row in caregiver_rows:
            caregiver_info.append(str(row['caregiver_info']))

    
    # For a GET request, we fetch the car info and caregiver info and render the template.
    if request.method == "GET":
        fetch_car_info()
        fetch_caregiver_info()
        return render_template("add_driver_junior.html", existing_cars=car_info, existing_caregiver=caregiver_info)

    # For a POST request, we first handle the form submission by inserting the new driver.
    elif request.method == "POST":
        driver_firstname = request.form['driver_firstname']
        driver_surname = request.form['driver_surname']
        driver_id = request.form['driver_id']
        car_num = request.form['car_model'].split(' ')[0]  # Getting car number
        caregiver_id=request.form['caregiver'].split(' ')[0] # Getting caregiver id
        birthdate_str=request.form['birthdate']    # Getting birthday
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')  # Parse string into date object
        today=datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        # Insert the new driver
        cursor.execute("""
            INSERT INTO driver (driver_id, first_name, surname, age, caregiver, car)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (driver_id, driver_firstname, driver_surname,age, caregiver_id,car_num))
        
        #update the run table
        crs_ids = ['A', 'B', 'C', 'D', 'E', 'F']
        for crs_id in crs_ids:
            for run_num in [1, 2]:
                cursor.execute("""
                    INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd)
                    VALUES (%s, %s, %s, NULL, NULL, 0)
                """, (driver_id, crs_id, run_num))
        
        # Important: Fetch the car info again before rendering the template.
        fetch_car_info()
        fetch_caregiver_info()
        return render_template("add_driver_junior.html", existing_cars=car_info,existing_caregiver=caregiver_info, message="Driver added successfully!")


if __name__ == "__main__":
    app.run(debug=True)
