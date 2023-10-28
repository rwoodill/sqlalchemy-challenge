# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///SurfsUp/Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = '2016-08-23'
    selection = [Measurement.date, Measurement.prcp]
    precip = session.query(*selection)\
            .filter(Measurement.date >= start_date)\
            .group_by(Measurement.date)\
            .order_by(Measurement.date).all()
    session.close()

    precip_dates = []
    precip_totals = []

    for date, daily_precip in precip:
        precip_dates.append(date)
        precip_totals.append(daily_precip)

    precip_dict = dict(zip(precip_dates, precip_totals))

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Station.station)\
                    .order_by(Station.station).all()
    session.close()

    station_results = list(np.ravel(results))

    return jsonify(station_results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_active_station = 'USC00519281'
    start_date= '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
    results = session.query(*sel)\
                    .filter(Measurement.date >= start_date)\
                    .filter(Measurement.station == most_active_station)\
                    .group_by(Measurement.date)\
                    .order_by(Measurement.date).all()
    session.close()
    
    observation_dates = []
    temperature_observations = []

    for date, observation in results:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict) 

@app.route("/api/v1.0/<start>")
def start_date_only(start, end_date='2017-08-23'):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end_date).all()
    session.close()

    stats = []
    for min, avg, max in result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        stats.append(trip_dict)

    if trip_dict['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date {start} not found or not formatted as YYYY-MM-DD."}), 404

@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end='2017-08-23'):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end).all()
    session.close()

    stats = []
    for min, avg, max in result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        stats.append(trip_dict)

    if trip_dict['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range, or not formatted as YYYY-MM-DD."}), 404   

if __name__ == '__main__':
    app.run(debug=True)