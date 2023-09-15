# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#session = Session(engine)


#################################################
# Flask Setup
app = Flask(__name__)


#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    start_date = dt.datetime.strptime(latest_date.date,'%Y-%m-%d').date()
    prev_yr = start_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_yr).all()
    session.close()

    precipitation = []
    for date, prcp in results:
            precip_dict ={}
            precip_dict['date'] = date
            precip_dict['prcp'] = prcp
            precipitation.append(precip_dict)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
# Create a session from python to the DB
    session = Session(engine)
    station_queries = session.query(Station.name, Station.station, Station.elevation).all()
    session.close()
    #create dictionary of stations
    list_of_stations = []
    for result in station_queries:
        row = {}
        row["name"] = result[0]
        row["station"] = result[1]
        row["elevation"] = result[2]
        list_of_stations.append(row)
      # Return a json list of stations
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# Starting from the most recent data point in the database.
    most_recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    starting_date = dt.datetime.strptime(most_recent_date.date, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    previous_year = starting_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    data_precip_scores = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= previous_year).all()
     # Close Session
    session.close()
    # Create a list of dictionaries with the date and temperature with for loop
    all_temperatures = []
    for date, temp in data_precip_scores:
        temp_information = {}
        temp_information['Date'] = date
        temp_information['Temperature'] = temp
        all_temperatures.append(temp_information)
    return jsonify(all_temperatures)

@app.route('/api/v1.0/temp/<start>')
def start(start):
    session = Session(engine)
    query_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    tobs_all = []
    for min,avg,max in query_results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route('/api/v1.0/temp/<start>/<end>')
def start_stop(start,end):
    session = Session(engine)
    query_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    tobs_all = []
    for min,avg,max in query_results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

if __name__ == "__main__":
    app.run(debug=True)