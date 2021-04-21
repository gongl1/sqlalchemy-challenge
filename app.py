import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>" # br line break
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    oneyearago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query all prcps in the last 12 months as I did in JupyterLab
    prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= oneyearago).\
        order_by(Measurement.date).all()
    # print(prcp) # This is a list of tuples
    # Convert list of tuples into a dictionary using dict()
    prcp_dict = dict(prcp)
    return jsonify(prcp_dict) # This is a dictionary



@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station = session.query(Measurement.station).\
        group_by(Measurement.station).all()
    print(station) # This is a list of tuples
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station))
    print(all_stations) # This is a normal list
    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data."""
    # Query all tobs in the last 12 months for the most active station as I did in JupyterLab
    oneyearago = dt.date(2017,8,23) - dt.timedelta(days=365)
    lasttwelvemonths_mostactive = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= oneyearago).\
    filter(Measurement.station == 'USC00519281').\
    order_by(Measurement.date).all()

    print(lasttwelvemonths_mostactive) # This is a list of tuples

    # Create a dictionary from the row data and append to a list of all_passengers
    all_tobs = []
    for datehi, tobshi in lasttwelvemonths_mostactive:
        tobs_dict = {}
        tobs_dict["date"] = datehi
        tobs_dict["tobs"] = tobshi
        all_tobs.append(tobs_dict) # Append every tobs_dict into list all_tobs
    print(all_tobs)
    return jsonify(all_tobs) # This is a list of dictionary with dict key so easier to read


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startend(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        print(results) # This is a list of tuples
        # Convert list of tuples into normal list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # Calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    print(results) # This is a list of tuples
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    print(temps) # This is a normal list
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
