
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# setup flask
app = Flask(__name__)


# setup routes

@app.route("/")
def home():
    """List all available api routes."""

    return (
        f"Welcome to the Home Page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br>"
        f"/api/v1.0/temp/<start>/<end>"
    )

### Routes

@app.route("/api/v1.0/precipitation")
def percipitation():

    """Return the precipitation data for the last year"""
    #find date from 12 months ago
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    last_12_months = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>=query_date).\
    order_by(Measurement.date).all()

    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    precip = {date: perc for date, perc in precipitation}
    return jsonify(precip)



@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tempMonth():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    query_data = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_data).all()

    # Unravel results into a 1D array and convert to a list
    tempObs = list(np.ravel(results))

    # Return the results
    return jsonify(tempObs)
  
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    if not end:
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        results = session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) >= start).all()
        tempObs = list(np.ravel(results))

        # Return the results
        return jsonify(tempObs)

    
    results = session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) >= start).all().\
        filter(func.strftime("%m-%d", Measurement.date) <= end).all()
    tempObs = list(np.ravel(results))

    # Return the results
    return jsonify(tempObs)

if __name__ == '__main__':
    app.run(debug=True)
