# 10_SQL_Alchemy_Project

This project takes a sqlite database containing weather station data and conducts analysis on the database using SQL Alchemy. In this project, I reflected the database to extract/save table references and then was able to create a session to connect to the database using Python/SQL Alchemy. Within the database, there are 2 tables (Measurement and Station), which could be queried for various datapoints. This project focused on the most recent 12 months of data from the database, looking at precipitation and temperature data. Finally, I created a Flask application in order to display various pieces of information in JSON format, with 2 routes dependent on user-input for generating a date-range to query. 

Flask App Notes
- 

The flask app provide information about each route directly within the app/browser when you first load it. 

Precipitation route utilizes average daily precipitation. This was done in order to provide valid info for each day in the last 12 months and take the average of the multiple stations that reported for each day. Averaging will be easier to scale over time (if stations are removed/added) and also provides a value more comparable to a single station (rather than summing). 

Start Route and Start/End Date Route both require user input in YYYY-MM-DD format

Code Source
- 
During exploratory precipitation analysis, I used .fromisoformat() in order to convert date into usable datetime format for manipulation. This method was introduced to me during a tutoring session. 
https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat

During exploratory station analyis, I originally utilized a .distinct().count() method to calculate the number of stations. Working with a tutor, it was suggested to align query with SQL functionality by doing the functions within the query, so I moved my query to use func.count(distinct()). Both are workable solutions are are provided below, but I did have to update dependencies for SQL Alchemy to include distinct: 
Original query: 
session.query(Measurement.station).distinct().count()
Updated query: 
session.query(func.count(distinct(Measurement.station))).scalar()

Additonally, the tutor introduced me to the scalar method in order to strip the list/tuple groupings from query results for a single result (displays first element of first result). 
https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.scalar

In the code for the flask app, I utilized a g-object in order to use the date 12 months prior to the most recent date in 2 different routes (precipitation and tobs). A Learning Assistant helped determine this method of using a variable across routes to avoid duplication of code within each route without using global variables which pose a security risk in flask apps/routes. In order to do this, I imported the additional dependency of 'g' from flask. The assistant helped provide the structure for the before_request app 



