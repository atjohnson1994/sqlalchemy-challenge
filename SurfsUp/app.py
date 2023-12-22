# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start session
    session = Session(engine)

    # Calculate last date in dataset
    starting_point = session.query(measurement.date).order_by(measurement.date.desc()).first()
    starting_point =starting_point[0]

    # Calculate one year of data from last date in dataset
    y = int(starting_point[:4])
    m = int(starting_point[6:7])
    d = int(starting_point[-2:])
    starting_point = dt.date(y,m,d)
    ending_point = starting_point - dt.timedelta(days=365)

    # Query precipiation data in date range
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date >= ending_point).all()
    
    # Close session
    session.close()

    # Create a dictionary from precipitation data
    prcp_values = []
    for date, prcp in results:
        date_value = {}
        date_value['date'] = date
        date_value['prcipitation'] = prcp
        prcp_values.append(date_value)

    # Return precipitation data in json format
    print("Server received request for 'precipitation' page...")
    return jsonify(prcp_values)
    


@app.route("/api/v1.0/stations")
def stations():
    # Start session
    session = Session(engine)
    station = Base.classes.station
    # Query station data
    results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    
    # Close session
    session.close()

    # Create a dictionary from station data
    station_dic = []
    for station, name, latitude, longitude, elevation in results:
        station_entry = {}
        station_entry['station'] = station
        station_entry['name'] = name
        station_entry['latitude'] = latitude
        station_entry['longitude'] = longitude
        station_entry['elevation'] = elevation
        station_dic.append(station_entry)

    # Return station data in json format
    print("Server received request for 'stations' page...")
    return jsonify(station_dic)



@app.route("/api/v1.0/tobs")
def tobs():
    # Start session
    session = Session(engine)

    # Calculate last date in dataset
    starting_point = session.query(measurement.date).order_by(measurement.date.desc()).first()
    starting_point =starting_point[0]

    # Calculate one year of data from last date in dataset
    y = int(starting_point[:4])
    m = int(starting_point[6:7])
    d = int(starting_point[-2:])
    starting_point = dt.date(y,m,d)
    ending_point = starting_point - dt.timedelta(days=365)

    # Calculate most active station
    station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station = station_activity[0][0]

    # Query tobs data
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date >= ending_point).filter(measurement.station == most_active_station).all()
    
    # Close session
    session.close()

    # Create a dictionary of tobs data
    tobs_dic = []
    for date, tobs in results:
        tobs_entry = {}
        tobs_entry['date'] = date
        tobs_entry['tobs'] = tobs
        tobs_dic.append(tobs_entry)

    # Return tobs data in json format
    print("Server received request for 'tobs' page...")
    return jsonify(tobs_dic)

@app.route("/api/v1.0/<start>")
def start(start):
    # Start session
    session = Session(engine)

    # Use specified date as last date
    ending_point = start.replace(" ","").lower()
    
    # Query temp data
    results = session.query(measurement.tobs).filter(measurement.date >= ending_point).all()
    
    start_min = np.min(results)
    start_max = np.max(results)
    start_avg = np.average(results)

    # Close session
    session.close()

    # Create a dictionary of tobs data
    start_dic = []
    start_entry = {}
    start_entry['min'] = start_min
    start_entry['max'] = start_max
    start_entry['avg'] = start_avg
    start_dic.append(start_entry)

    # Return tobs data in json format
    print("Server received request for 'start' page...")
    return jsonify(start_dic)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Start session
    session = Session(engine)

    # Use specified date as last date
    ending_point = start.replace(" ","").lower()
    starting_point = end.replace(" ","").lower()
    
    # Query temp data
    results = session.query(measurement.tobs).filter(measurement.date >= ending_point).filter(measurement.date <= starting_point).all()
    
    start_end_min = np.min(results)
    start_end_max = np.max(results)
    start_end_avg = np.average(results)

    # Close session
    session.close()

    # Create a dictionary of tobs data
    start_end_dic = []
    start_end_entry = {}
    start_end_entry['min'] = start_end_min
    start_end_entry['max'] = start_end_max
    start_end_entry['avg'] = start_end_avg
    start_end_dic.append(start_end_entry)

    # Return tobs data in json format
    print("Server received request for 'start to end' page...")
    return jsonify(start_end_dic)




if __name__ == '__main__':
    app.run(debug=True)

