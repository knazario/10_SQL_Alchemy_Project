# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
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
        f"<strong><u>Currently Available Routes:</u></strong><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<strong>START_DATE</strong>- User enters date in YYYY-MM-DD format<br/>"
        f"/api/v1.0/<strong>START_DATE/END_DATE</strong> -User enters start & end dates in YYYY-MM-DD format"
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    last12mo_date = dt.date(2017, 8, 23) - dt.timedelta(days =365)
    last12mo_df= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last12mo_date).all()
    dict = {}
    for date,percip in last12mo_df:
        dict[date] = percip

    return jsonify(dict)
    
@app.route("/api/v1.0/stations")
def stations():
    query = session.query(Measurement.station).distinct().all()
    station_list = list(np.ravel(query))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():


    return "Test"

@app.route("/api/v1.0/<start>")
def start():


    return "Test"

@app.route("/api/v1.0/<start>/<end>")
def start_end():


    return "Test"


if __name__ == '__main__':
    app.run(debug=True)
