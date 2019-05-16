import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.dates as mdates
import pprint
from flask import Flask, jsonify
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect() 

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurements = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
first_row = session.query(Measurements).first()
print(first_row.__dict__)
first_row_2 = session.query(Station).first()
print(first_row_2.__dict__)
latest = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
date_start_query = dt.date(2017, 8, 23) - dt.timedelta(days=365)


app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/&ltstart&gt, /api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt, /api/v1.0/2017-01-01/2017-01-04"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """
    Return dates and precipitation observations from the last year
    """
    results = session.query(Measurements.date, func.avg(Measurements.prcp)).filter(Measurements.date>=date_start_query).group_by(Measurements.date).all()

    results_list = []
    for date, prcp in results:
        results_list.append({str(date): prcp})
    return jsonify(results_list)
@app.route("/api/v1.0/stations")
def station():
    """
    Return stations
    """ 
    results = session.query(Station.station).all()
    results_list = list(np.ravel(results))
    return jsonify(results_list)
@app.route("/api/v1.0/tobs")
def tobs():
    """
    Return dates and temperature observations from the last year
    """  
    results = session.query(Measurements.date, func.avg(Measurements.tobs)). \
                filter(Measurements.date>=date_start_query). \
                group_by(Measurements.date).all()
    results_list = []
    for date, temp in results:
        results_list.append({str(date): temp})
    return jsonify(results_list)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end=latest):
    '''
    Return the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
    '''
    start_date_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    if end == latest:
        end_date_dt = end
    else:
        end_date_dt = dt.datetime.strptime(end, '%Y-%m-%d')
    sel = [func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]
    temps = session.query(*sel). \
                filter(Measurements.date>=start_date_dt). \
                filter(Measurements.date<=end_date_dt).all()[0]
    results_list = [{"temp_min": temps[0]}, 
                    {"temp_avg": temps[1]}, 
                    {"temp_max": temps[2]}]
    return jsonify(results_list)
if __name__ == '__main__':
    app.run(debug=False)