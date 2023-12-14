# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return the precipitation for the last year"""
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= dt.datetime(2016,8,23)).all()
    prec_list = []
    for date, prcp in results:
        prec_dict = {
            'date': date,
            'prcp': prcp
        }
        prec_list.append(prec_dict)
    
    return jsonify(prec_list)

@app.route('/api/v1.0/stations')
def stations():
    """Return all of the stations"""
    station_list = session.query(station.name).distinct().all()
    all_stations = list(np.ravel(station_list))

    return jsonify(all_stations)

@app.route('/api/v1.0/tobs')
def tobs():
    """Return a list of temperature observations from the most active station last year"""
    temperatures = (
    session.query(measurement.tobs)
    .filter(measurement.date > dt.datetime(2016,8,23)).
    filter(measurement.station == 'USC00519281')
    .all())

    temperatures = [temp[0] for temp in temperatures]

    return jsonify(temperatures)

@app.route('/api/v1.0/<start>')
def start_search(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    result = (
        session.query(
            func.min(measurement.tobs).label('min_tobs'),
            func.avg(measurement.tobs).label('avg_tobs'),
            func.max(measurement.tobs).label('max_tobs')
        )
        .filter(measurement.date >= start_date)
        .all()
    )

    data = {
        'tmin': result[0].min_tobs,
        'tavg': result[0].avg_tobs,
        'tmax': result[0].max_tobs
    }

    return jsonify(data)

@app.route('/api/v1.0/<start>/<end>')
def start_end_search(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    result = (
        session.query(
            func.min(measurement.tobs).label('min_tobs'),
            func.avg(measurement.tobs).label('avg_tobs'),
            func.max(measurement.tobs).label('max_tobs')
        )
        .filter(measurement.date >= start_date, measurement.date <= end_date)
        .all()
    )
    
    data = {
        'tmin': result[0].min_tobs,
        'tavg': result[0].avg_tobs,
        'tmax': result[0].max_tobs
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)