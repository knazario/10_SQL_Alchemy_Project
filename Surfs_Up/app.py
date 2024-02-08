# Import the dependencies.
from flask import Flask, jsonify
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

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create app
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
# Define index route.
@app.route("/")
def home():
    return ( 
        # print/return strings for all available routes, using <strong> to emphasize user input needed. Added direct url links for routes without user-input
        f"<strong><u>Currently Available Routes:</u></strong><br/><br/>"
        
        f"Precipitation Route- Relative URL: <a href = '/api/v1.0/precipitation'> /api/v1.0/precipitation</a><br/><br/>"
        
        f"Stations Route- Relative URL: <a href = '/api/v1.0/stations'>/api/v1.0/stations</a><br/><br/>"
        
        f"Temperature Route- Relative URL:<a href = '/api/v1.0/tobs'>/api/v1.0/tobs</a><br/><br/>"
        
        f"Start Date Route- Relative URL:/api/v1.0/<strong>START_DATE</strong><br/>\
        User enters start date in YYYY-MM-DD format. \
        Valid Date Range: (2016-08-23 - 2017-08-23)<br/>\
        The Start Date Route displays the minimum temperature, average temperature, and max temperature for the date range of \
        user-entered start date to the end of the dataset (2017-08-23)<br/><br/>"
        
        f"Start Date/End Date Route- Relative URL:/api/v1.0/<strong>START_DATE/END_DATE</strong> <br/>\
        User enters start & end dates in YYYY-MM-DD format.\
        Valid Date Range: (2016-08-23 - 2017-08-23)<br/>\
        The Start Date/End Date Route displays the minimum temperature, average temperature, and max temperature\
        for the date range of user-entered start date to the user-entered end date"
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #query most recent date in dataset using max function
    recent_date = session.query(func.max(Measurement.date)).scalar()
    #create dt.date variable for date 12 months prior to most recent date
    last12mo_date = dt.date.fromisoformat(recent_date) - dt.timedelta(days =365)
    #query last 12 months of precipitation data, grouping by date to get daily average precipitation from reporting stations
    last12mo_df= session.query(Measurement.date, func.round(func.avg(Measurement.prcp),2))\
        .filter(Measurement.date >= last12mo_date).group_by(Measurement.date).all()

    #Use for loop/dictionary comprehenstion in order to create a dictionary with the date as key, and percip as value
    rain_dict = {date:percip for date,percip in last12mo_df}
    
    #return dictionary in json format
    return jsonify(rain_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    query = session.query(Measurement.station).distinct().all()
    station_list = list(np.ravel(query))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(func.max(Measurement.date)).scalar()
    last12mo_date = dt.date.fromisoformat(recent_date) - dt.timedelta(days =365)
    most_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).limit(1).scalar()

    # Query last 12 months of data, extracting date and temperature datapoints
    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last12mo_date).filter(Measurement.station == most_active).all()
    temp_list= [temp for date,temp in data]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    search_date = dt.date.fromisoformat(start)
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= search_date).all()
    temp_stats = list(np.ravel(temps))

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start, end):
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date)\
    .filter(Measurement.date <= end_date).all()
    temp_stats = list(np.ravel(temps))

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
