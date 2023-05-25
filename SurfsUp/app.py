#######################
# Import Dependencies #
#######################

import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

##################
# Database Setup #
##################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
Base.classes.keys()

# Save reference to the table
station = Base.classes.station
measurment = Base.classes.measurement

###############
# Flask Setup #
###############

app = Flask(__name__)

###############
# Flask Routes#
###############

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-08-18<br/>"
        f"/api/v1.0/2010-01-01/2010-01-27<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns the precipitation data for the last year in the database """

    # Perform a query to retrieve the data and precipitation scores
    # Find the most recent date in the data set.
    last_date = session.query(measurment.date).order_by(measurment.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(measurment.date,measurment.prcp).filter(measurment.date >= query_date , measurment.prcp != 'None').all()

    #Close Session
    session.close()

    # Create a dictionary from the row data and append to a list of date and percipitation data
    percipitation_data = []
    for date,prcp in results:
        percipitation_data_dict = {}
        percipitation_data_dict["date"] = date
        percipitation_data_dict["prcp"] = prcp
        percipitation_data.append(percipitation_data_dict)

    return jsonify(percipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(station.station).all()
    #Close session
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns the temperature data of most active station for the last year in the database """

    # Perform a query to retrieve the data and temperature scores
   
    #retrieve the most active station
    sel = [measurment.station,func.count(measurment.station)]
    active_station = session.query(*sel).\
    group_by(measurment.station).\
    order_by(func.count(measurment.station).desc()).all()
    
    (most_active,totalcount) = active_station[0]
    
    #Retrieve the last date
    last_date = session.query(measurment.date).filter(measurment.station == most_active).order_by(measurment.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    query_date1 = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    results = session.query(measurment.date,measurment.tobs).filter(measurment.station == most_active , measurment.date >= query_date1).all()

    #Close Session
    session.close()

    # Create a dictionary from the row data and append to a list of date and temperature data
    temperature_data = []
    for date,tobs in results:
        temperature_data_dict = {}
        temperature_data_dict["date"] = date
        temperature_data_dict["tobs"] = tobs
        temperature_data.append(temperature_data_dict)

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def temp_startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, 
       and the maximum temperature for a specified start date"""
    
    results = session.query(func.min(measurment.tobs),func.max(measurment.tobs),func.avg(measurment.tobs)).filter(measurment.date >= start).all()

    session.close()
    
    # Create a dictionary from the row data and append to min,amx and avg temp for the specified start date
    summary_data = []
    for tmin,tmax,tavg in results:
        summary_data_dict = {}
        summary_data_dict["Min"] = tmin
        summary_data_dict["Max"] = tmax
        summary_data_dict["Avg"] = tavg
        summary_data.append(summary_data_dict)

    return jsonify(summary_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_startenddate(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, 
       and the maximum temperature for a specified start date and end date."""
    
    results = session.query(func.min(measurment.tobs),func.max(measurment.tobs),func.avg(measurment.tobs)).filter(measurment.date >= start ,measurment.date <= end ).all()
    session.close()
    
    # Create a dictionary from the row data and append to min,amx and avg temp for the specified start/end  date
    summary_data = []
    for tmin,tmax,tavg in results:
        summary_data_dict = {}
        summary_data_dict["Min"] = tmin
        summary_data_dict["Max"] = tmax
        summary_data_dict["Avg"] = tavg
        summary_data.append(summary_data_dict)

    return jsonify(summary_data)

if __name__ == "__main__":
    app.run(debug=True)
