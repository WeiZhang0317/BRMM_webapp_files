# BRMM_webapp_files

## 1. Web application structure
Route and Function:

### 1.1 List of courses
#### Route: @app.route("/listcourses")  
#### Function: listcourses()   getCursor()
#### Template: courselist.html  
#### Data: motorkhana database course table, the course_id name and image
#### Relationship:
The route /listcourses is directly related to the listcourses() function. When this route is accessed by a user through their web browser, it triggers the execution of listcourses().

This function connects to motorkhana database course table, retrieves all entries from the 'course' table in the database:  the course_id name and image, and then sends this data to the template "courselist.html" for rendering.

The data is stored in courseList, which is a list of tuples, where each tuple represents a row from the 'course' table in the database. This courseList is passed to the "courselist.html" template as course_list.


### 1.2 Driver’s run details
####  Route: @app.route("/driverdetails")
####  Function: driverdetails() getCursor()
####  Template: driverdetails.html
####  Data: motorkhana database - driver, run, course, car tables
#### Relationship:
The route /driverdetails is directly related to the driverdetails() function. When this route is accessed by a user through their web browser, it triggers the execution of driverdetails().

If it's a "GET" request and there's no driver name in the URL, the function fetches all driver names and displays an initial form with a dropdown menu, allowing the user to select a driver's name. The names are fetched using data (first name and surname) from the 'driver' table.

If it's a "POST" request or if a driver's name is specified, the function will either return the initial form with driver names (if the "return" button was pressed)  or the function will proceed to fetch detailed information about the selected driver. The information joins multiple tables (driver, run, course, car). It's sent to the "driverdetails.html" template for rendering. The data is stored in driver_details, which is a list of dictionaries.



