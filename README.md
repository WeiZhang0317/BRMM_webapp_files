# BRMM_webapp_files

## 1. Web application structure

### 1.1 List of courses
#### Route: @app.route("/listcourses")  
#### Function: listcourses()   getCursor()
#### Template: courselist.html  
#### Data: motorkhana database course table, 
the course_id name and image
#### Relationship:
The route /listcourses is directly related to the listcourses() function. When this route is accessed by a user through their web browser, it triggers the execution of listcourses().

This function connects to motorkhana database course table, retrieves all entries from the 'course' table in the database:  the course_id name and image, and then sends this data to the template "courselist.html" for rendering.

The data is stored in courseList, which is a list of tuples, where each tuple represents a row from the 'course' table in the database. This courseList is passed to the "courselist.html" template as course_list.


### 1.2 Driver’s run details
####  Route: @app.route("/driverdetails" methods=["GET", "POST"])
####  Function: driverdetails() getCursor()
####  Template: driverdetails.html
####  Data: motorkhana database - driver, run, course, car tables
driver: first name and surname, course: course name, car: car model and drive class, run: run num, second, cones and wd
#### Relationship:
The route /driverdetails is directly related to the driverdetails() function. When this route is accessed by a user through their web browser, it triggers the execution of driverdetails().

If it's a "GET" request and there's no driver name in the URL, the function fetches all driver names and displays an initial form with a dropdown menu, allowing the user to select a driver's name. The names are fetched using data (first name and surname) from the 'driver' table.

If it's a "POST" request or if a driver's name is specified, the function will either return the initial form with driver names (if the "return" button was pressed)  or the function will proceed to fetch detailed information about the selected driver. The information joins multiple tables (driver, run, course, car). It's sent to the "driverdetails.html" template for rendering. The data is stored in driver_details, which is a list of dictionaries.

### 1.3 List of drivers
#### Route: @app.route("/listdrivers")
#### Function: listdrivers() getCursor()
#### Template: listdrivers.html
#### Data: motorkhana database - driver and car tables， 
driver-first name and surname, car-car model, and drive class
#### Relationship:

Inside the function listdrivers() , it retries data from the database. The data comes from the 'driver' and 'car' tables, including names, car models, and driving classes. After retrieval, the data is stored in a list of tuples named driver_details. This list is then passed to the listdrivers.html template via the drivers context variable.
The listdrivers.html template: It iterates over its contents to display each driver's details on the webpage.
Driver names in the table serve as links to selected driver's deatails (/driverdetails).

### 1.4 Overallresults
#### Route: @app.route("/overallresults")
#### Function: overallresults() fetch_overallresults() getCursor()
#### Template: overallresults.html
#### Data: motorkhana database - tables including 'driver', 'run', 'course', and 'car'
driver:driver_id, first_name, surname,course: name, run: run_num, seconds, cones,wd,
car: model, drive_class 

#### Relationship:
The overallresults() function, is triggered by accessing the /overallresults route.

By calling fetch_overallresults() executes a SQL query. It calculates overall result for each driver, etc.

The gathered data, representing various aspects like the fastest times and overall scores is organized into a list of tuples known as overallResults. This overallResults data is then send to the "overallresults.html" template. 

Moreover, the template has a direct link for visual performance analytics (See Top5 Driver's Graph)

###  1.5 Bar graph
#### Route: @app.route("/graph")
#### Function: showgraph() fetch_overallresults()
#### Template: top5graph.html
#### Data: motorkhana database - tables including 'driver', 'run', 'course', and 'car'
driver:driver_id, first_name, surname,course: name, run: run_num, seconds, cones,wd,
car: model, drive_class 
 
showgraph() calls fetch_overallresults() to get data from the database.

The function picks the top 5 results from the fetched data.

It prepares two lists: one for the drivers' names (bestDriverList) and one for their scores (resultslist).
These lists are sent to the top5graph.html template.

The template uses Plotly to create a graph showing the top performances.
The names list forms the Y-axis, and the scores list forms the X-axis of the graph.

### 1.6 Administrator Interface
#### Route: @app.route("/admin_interface")
#### Function: admin_interface()
#### Template: admin_interface.html
#### Data: No direct database interaction occurs in this function.

The function admin_interface() renders the 'admin_interface.html' template, providing no direct data interaction. The template outlines administrative tasks, each linked to different application routes using Flask's 'url_for' function.

### 1.7 Junior driver list
#### Route: @app.route("/juniordriverlist")
#### Function: juniordriverlist() getCursor()
#### Template: juniordriverlist.html
#### Data: Motorkhana database - 'driver' table

The juniordriverlist() function interacts with the 'driver' table to retrieve information about junior drivers. It executes a SQL query to fetch details like driver's name, date of birth, age, and caregiver information. 

After fetching and refining the data, a list of junior drivers is compiled, list is passed to the 'juniordriverlist.html' template.

The template constructs a table displaying the junior drivers' details, with a navigation link back to the Admin Interface. 


### 1.8 Driver search
#### Route: @app.route("/searchname" methods=["GET", "POST"])
#### Function: searchname() getCursor()
#### Template: searchname.html
#### Data: Motorkhana database - 'driver' table

The function searchname() can handle both GET and POST methods for form submission. When the form is submitted (POST request), it takes the keyword input for driver's name, and searches in the 'driver' table of the database for matches by first or last name.

These results are then sent to the 'searchname.html' template. The template includes a form that allows users to input a search keyword for driver's name. 

The template extends the basic structure from "admin_interface.html" and includes a link to navigate back to the main Admin Interface.

### 1.9 Edit runs
#### Route: @app.route("/edit_runs")
#### Function: edit_runs()
#### Template: edit_runs.html
#### Data: No direct database interaction occurs in this function.
The edit_runs() function renders the "edit_runs.html" template. This template is extends from "admin_interface.html".

Within the "edit_runs.html" template, there's a navigational section presented as a list with two links, allowing the user to choose between editing runs by driver or by course. These links, 'Choose a driver to edit runs' and 'Choose a course to edit runs', redirect to the respective routes edit_runs_driver and edit_runs_course.

###  1.9.1 Edit runs driver
#### Route: @app.route("/edit_runs_driver" methods=["GET", "POST"])
#### Function: edit_runs_driver()
#### Template: edit_runs_driver.html
#### Data: driver Table, run Table, course Table

GET Request:

Displays a list of all drivers' names in a dropdown menu on the "edit_runs_driver.html" page for users to select and view detailed information.

POST Request: 

Edit Button: Updates the database with new run details entered by the user, including metrics like 'seconds', 'cones', and 'wd'. The page is refreshed to show updated data.

Driver Selection: When a driver is chosen, detailed information about their runs is retrieved and displayed, allowing for editing.

Return Button: Refreshes the page by redirecting users to the same page.

###  1.9.2 Edit runs course
#### Route: @app.route("/edit_runs_course" methods=["GET", "POST"])
#### Function: edit_runs_course()
#### Template: edit_runs_course.html
#### Data: Motorkhana database - driver Table, run Table, course Table
course Table: Includes details like course_id and name.
driver Table: Contains information such as driver_id, first_name, and surname.
run Table: references to the course and driver tables through crs_id and dr_id, along with performance data like seconds, cones, and wd.

GET Request:

Retrieves a list of all course names from the database.
Displays the course names in a dropdown menu on the template.

POST Request:

Refreshes the page if the 'return' button is clicked.
Updates run details (like 'seconds', 'cones', 'wd') in the database based on user input when the 'edit' button is clicked..
Retrieves and displays detailed run information for a specific course selected from the dropdown menu.

###  1.10 Add driver
#### Route:@app.route(/add_driver)
#### Function: add_driver()
#### Template: add_driver.html
#### Data: No direct database interaction occurs in this function.

The template extends a base layout template, admin_interface.html.

admin_interface.html has two navigation links are provided:
"Add Adult Driver" links to the route for adding adult drivers (add_driver_adult).
"Add Junior Driver" links to the route for adding junior drivers (add_driver_junior).
A button to navigate back to the main admin interface.

###  1.10.1 Add driver adult
#### Route: @app.route("/add_driver_adult", methods=["GET", "POST"])
#### Function: add_driver_adult(), getCursor(), fetch_car_info()
#### Template:add_driver_adult.html
#### Data: Motorkhana database - 'car' table, 'driver' table, 'run' table
The function add_driver_adult() is designed to handle both GET and POST requests for the form used to add an adult driver's information to the database.

During a GET request, the function calls fetch_car_info() to retrieve available cars' information from the 'car' table. It then renders the template add_driver_adult.html, passing the car information.

For a POST request (form submission), the function extracting the new driver's details. These details are then inserted into the 'driver' table, and new records are created in the 'run' table corresponding to this driver. Finally, it fetches the car info again and renders the same template.

The add_driver_adult.html template extends from the add_driver.html base template.
Upon successful form submission, a message is displayed to the user.
The template includes a link to navigate back to the 'add_driver' page.

###  1.10.2 Add driver junior
#### Route: @app.route("/add_driver_junior", methods=["GET", "POST"])
#### Function: add_driver_junior(), getCursor(), fetch_car_info(), fetch_caregiver_info()
#### Template: add_driver_junior.html
#### Data: Motorkhana database - 'car' table, 'driver' table, 'run' table
GET Request: 

Displays the form, pre-filled with data from the 'car' and 'driver' tables.

POST Request:

Processes form data, calculates the junior driver's age, updates the 'driver' and 'run' tables, and shows a confirmation message.

The add_driver_junior.html template features:

Form inputs for entering specific driver information.Dynamic lists for caregiver and car selection.Upon successful form submission, a message is displayed to the user.Navigation link to the add driver homepage.

## 2.Assumptions and design decisions:
####  2.1 Separate functional interface
######   Assumptions:

I assume that each Functional requirement has its own interface, which helps reduce confusion. It is assumed that the user has basic knowledge of using drop-down menus, submitting forms, etc. 

######   Design decisions:
In the design of the web page, I tried to make each requirement correspond to a template and route, but for "edit runs" and "add drivers", I designed multiple sub-routes.

For the "Edit runs" I created three different templates and corresponding routes to reflect the different editing options. these are:

edit_runs.html: Overview page, providing two editing options, users can find the item they want to edit through the driver or course drop-down menu.
edit_runs_course.html: Based on the course drop-down menu selection
edit_runs_driver.html: based on driver dropdown selection
Although the forms displayed by these two editor selections are the same, which is multiple similar pages, administrators can find them easily and directly when they have different search needs.

For "Add Driver", three templates and routes are also designed to handle different types of driver addition operations, as follows:

add_driver.html: This is a navigation page that provides the user with two options: add a junior driver or an adult driver.
add_driver_adult.html: Detailed form page for adding an adult driver.
add_driver_junior.html: The corresponding form page for adding junior drivers.
This way, I was able to ensure that each specific task had a clearly defined path, while retaining the simplicity of the interface, allowing users to intuitively find the specific task they needed to complete.

####  2.2 Data input

######   Assumptions:

In the requirements of edit run and add driver, I assume that all user input should be validated by the front end to keep the database from generating errors.

######   Design decisions:

In the edit run function, I limited the input second to a number with two decimal places, and wd and cones to be integers. In the add driver function, I restricted the input of the name to text and the input of driver ID to numbers. In order to ensure that the age of the junior driver is within the restricted range, the user is only allowed to select date of birth from "1998-01-01" to "2023-12-12"


####  2.3 Table Design


######   Assumptions:

For Driver List, the task requires modifying the /listdrivers route so that it displays the car details associated with each driver. In the document, it is not specified what exactly the "details of the car" should contain. So I assume some basic and generally relevant information like "car model" and "driver class" should be included. Similarly, the driver run details task request does not provide a detailed list header, but only requires “driver’s run details”. I assumed that these run details should be data related to calculating the run total.


######   Design decisions:

In response to the updated demand for the "driver list", I adjusted the content related to the /listdrivers route. When designing the table, I made assumptions based on general car-related information and decided to include the car model and driver class.

For the "driver run details" section, based on the task needed to list the "run total", I decided to add the relevant fields needed to calculate the "run total" in the table, such as "cones", "seconds", "wd", etc. This design choice was made to ensure that the table provides enough data for users to see and understand the complete results of each run.

####  2.4 Template repeatability:
######   Design decisions:

To maintain consistency across the application, certain page templates are reused. For example, 'base.html' and 'admin_interface.html' ensure a unified appearance.

Similarly, both the edit driver and the edit course use the drop-down menu to select the driver or course from the menu to make modifications, instead of combining the functions of the search driver and the edit driver. This is to maintain the consistency of the interface, and when the user only wants simple and intuitive operations are also possible when performing a single operation (only querying names rather than modifying related content)

####  2.5 Navigation and Layout
######   Design decisions:
When designing the drop-down menu, I added a "return" back button and a "back to admin interface" option in the relevant pages of the admin interface to ensure that users can navigate freely on a certain page.

####  2.6 GET and POST methods
######   Design decisions:
GET requests are used to retrieve and display data from a database and are useful when the user navigates to a page that displays data such as a driver list or course details. When users submit edited/added data or selected driver/course etc through forms, use POST requests to provide secure data transmission.

####  2.7 Feedback and Confirmation:
######   Design decisions:
After operations such as adding, feedback "Driver added successfully!" is provided to the user. This design gives users the confidence to take the next step.

####  2.8 Database Query Optimization
######   Design decisions:
Functions like fetch_overallresults() are used, which means the data processing is handled mainly within the database (through SQL queries), instead of retrieving large data sets and processing them in app.py. This decision reduces the computational load on the web server.


####  2.9 Navigation to related content
######   Design decisions:
A link to the graph is designed on the overall result page so that users can see an intuitive graph after searching for the overall result without returning to the main interface.

## 3. Database questions

######   1. What SQL statement creates the car table and defines its three fields/columns? 

######   2. Which line of SQL code sets up the relationship between the car and driver tables?
######   3. Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?
######   4. Suppose the club wanted to set a default value of ‘RWD’ for the driver_class field. What specific change would you need to make to the SQL to do this? 
######   5. Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
