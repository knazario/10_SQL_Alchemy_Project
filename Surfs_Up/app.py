# Import the dependencies.
from flask import Flask, g, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt
#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link/bind) connecting Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create app
app = Flask(__name__)

#################################################
#Create function to calculate variables to be used across multiple routes (precipitation and tobs)
def get_recent_date():
    #query most recent date in dataset using max function
    recent_date = session.query(func.max(Measurement.date)).scalar()
    #create dt.date variable for date 12 months prior to most recent date
    last12mo_date = dt.date.fromisoformat(recent_date) - dt.timedelta(days =365)

    return last12mo_date

#Use before_request to create g object containing my date variable for use in multiple routes
@app.before_request
def get_variables():
    #assign g object to recent date by calling get_recent_date function (above)
    g.last12mo_date = get_recent_date()

#################################################
# Flask Routes
#################################################
# Define index route.
@app.route("/")
def home():
    return ( 
        # print/return strings for all available routes, using <strong> to emphasize user input needed. Added direct url links for routes without user-input
        f"<strong>Welcome to the Surfs Up API. You can access a variety of weather data following the routes below.<br/>\
        Current Data is from the following 12 month date span: 08/23/206 - 08/23/2017<br/>\
        All data is provided in JSON format.</strong><br/><br/>"        
        f"<strong><u>Currently Available Routes:</u></strong><br/><br/>"
        
        f"Precipitation Route: <a href = '/api/v1.0/precipitation'> /api/v1.0/precipitation</a>\
        <p style='margin-left: 25px;'> This route provides a dictionary of <strong>average</strong> daily precipitation data for 12 months of weather data\
        and the stations that provided data each day (we did not recevie data from all stations every day). </p>"
        f"******************************************************************<br/>"
        f"Stations Route:  <a href = '/api/v1.0/stations'>/api/v1.0/stations</a>\
        <p style='margin-left: 25px;'>This route provides a list of the reporting stations.</p>"
        f"******************************************************************<br/>"
        f"Temperature Route:<a href = '/api/v1.0/tobs'>/api/v1.0/tobs</a>\
        <p style='margin-left: 25px;'>This route provides a list of temperatures from the most active station during the 12 month period (USC00519281)</p>"
        f"******************************************************************<br/>"
        f"Start Date Route: /api/v1.0/<strong>START_DATE</strong>\
        <p style='margin-left: 25px;'>User enters start date in YYYY-MM-DD format. \
        Valid Date Range: (2016-08-23 - 2017-08-23)<br/>\
        The Start Date Route displays the minimum temperature, average temperature, and max temperature for the date range of \
        user-entered start date to the end of the dataset (2017-08-23)</p>"
        f"******************************************************************<br/>"
        f"Start Date/End Date Route: /api/v1.0/<strong>START_DATE/END_DATE</strong>\
        <p style='margin-left: 25px;'> User enters start & end dates in YYYY-MM-DD format.\
        Valid Date Range: (2016-08-23 - 2017-08-23)<br/>\
        The Start Date/End Date Route displays the minimum temperature, average temperature, and max temperature\
        for the date range of user-entered start date to the user-entered end date</p>"
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #query last 12 months of precipitation data, grouping by date to get daily average precipitation from reporting stations
    last12mo_df= session.query(Measurement.date, func.round(func.avg(Measurement.prcp),2))\
        .filter(Measurement.date >= g.last12mo_date).group_by(Measurement.date).all()

    #Use for loop/dictionary comprehenstion in order to create a dictionary with the date as key, and percip as value
    rain_dict = {date:percip for date,percip in last12mo_df}
    
    #return dictionary of percipitation data in json format
    return jsonify(rain_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    #Query Measurement table (could have also used station table) to pull distinct stations
    query = session.query(Measurement.station).distinct().all()
    # convert list of tuples into list of strings
    station_list = list(np.ravel(query))

    #return list of stations in json format
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # create query to display the most acitve station by sorting stations by row count and limiting search to top 1
    most_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).limit(1).scalar()

    # Query last 12 months of data for most active station, extracting date and temperature datapoints
    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= g.last12mo_date).filter(Measurement.station == most_active).all()
    #extract the temperature data and save as a list 
    temp_list= [temp for date,temp in data]

    #return the list of temperatures in json format
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    #covert the user-entered start-date into datetime format needed for query
    search_date = dt.date.fromisoformat(start)
    #query min temperature, average temp and max temp for dates between the user-entered 
    #start date and the most recent date in dataset (greater than or equal to) 
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= search_date).all()
    #convert list of tuples into list of values (min, avg, max) 
    temp_stats = list(np.ravel(temps))

    # return list in json format for display
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    #covert the user-entered start-date and end-date into datetime format needed for query
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)    
    #query min temperature, average temp and max temp for dates between the user-entered 
    #start date and user-entered end date 
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date)\
    .filter(Measurement.date <= end_date).all()
    #convert list of tuples into list of values (min, avg, max) 
    temp_stats = list(np.ravel(temps))

    #return list in json format for display
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
