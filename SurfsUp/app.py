# Rachel Woodill - Oct 27, 2023

# Import the dependencies
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

#################################################
# Route for home
#################################################
@app.route("/")
def welcome():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"Temperature observations for one year: /api/v1.0/tobs<br/>"
        f"Temperature statistics from the start date (YYYY-MM-DD): /api/v1.0/<start><br/>"
        f"Temperature statistics from between two dates (YYYY-MM-DD): /api/v1.0/<start>/<end>"
    )

#################################################
# Route for /api/v1.0/precipitation
# Displays the last 12 months of data in json format
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = '2016-08-23'
    selection = [Measurement.date, Measurement.prcp]
    
    # Query the db for the date and precipitation values, filtering by the start date
    # Also group by the date and order by the date
    precip = session.query(*selection)\
            .filter(Measurement.date >= start_date)\
            .group_by(Measurement.date)\
            .order_by(Measurement.date).all()
    
    # Close the session
    session.close()

    precip_dates = []
    precip_totals = []

    # Store the values in two lists
    for date, daily_precip in precip:
        precip_dates.append(date)
        precip_totals.append(daily_precip)

    # Zip into a dictionary
    precip_dict = dict(zip(precip_dates, precip_totals))

    return jsonify(precip_dict)

#################################################
# Route for /api/v1.0/stations
# Returns a json list of stations
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the db for the stations (order by station)
    results = session.query(Station.station)\
                    .order_by(Station.station).all()
    
    # Close the session
    session.close()

    # Flatten the array
    station_results = list(np.ravel(results))

    return jsonify(station_results)

#################################################
# Route for /api/v1.0/tobs
# Returns a json list of temperature observations (for previous year)
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_active_station = 'USC00519281'
    start_date= '2016-08-23'
    sel = [Measurement.date, 
        Measurement.tobs]
   
    # Query the db for dates and temp. observations, filtering by start date
    # and filtering by the most active station. Group by date and order by date
    results = session.query(*sel)\
                    .filter(Measurement.date >= start_date)\
                    .filter(Measurement.station == most_active_station)\
                    .group_by(Measurement.date)\
                    .order_by(Measurement.date).all()
    
    # Close the session
    session.close()
    
    observation_dates = []
    temperature_observations = []

    # Store the values in two lists
    for date, observation in results:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    # Zip into dictionary
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict) 

#################################################
# Route for /api/v1.0/<start>
# Enter a date in YYYY-MM-DD format and receive a json list of min. temp., average temp.,
# and max temp. for the date range. (end date = 2017-08-23)
#################################################
@app.route("/api/v1.0/<start>")
def start_date_only(start, end_date='2017-08-23'):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the db for the min, average, and max temperature oberservations
    # Filter by the start and end date (no end date given = 2017-08-23)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end_date).all()
    
    # Close the session
    session.close()

    stats = []
    # Store the values in a dictionary, then append to a list
    for min, avg, max in result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        stats.append(trip_dict)

    # If data exists return it as a json
    if trip_dict['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date {start} not found or not formatted as YYYY-MM-DD."}), 404

#################################################
# Route for /api/v1.0/<start>/<end>
# Enter a start date (YYYY-MM-DD) "/" and an end date (YYYY-MM-DD) to receive a
# json list of min. temp., average temp., and max temp. for the date range. 
# #################################################
@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end='2017-08-23'):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the db for the min, average, and max temperature oberservations
    # Filter by the start and end date (no end date given = 2017-08-23)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end).all()
    
    # Close the session
    session.close()

    stats = []
    # Store the values in a dictionary, then append to a list
    for min, avg, max in result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        stats.append(trip_dict)

    # If data exists return it as a json
    if trip_dict['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range, or not formatted as YYYY-MM-DD."}), 404   

#################################################
# Run the app
# #################################################
if __name__ == '__main__':
    app.run(debug=True)