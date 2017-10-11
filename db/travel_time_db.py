import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from obspy.taup import TauPyModel
from obspy.geodetics.base import kilometer2degrees
from phasepapy.associator.tt_stations_1D import BaseTT1D, TTtable1D

DB = os.path.dirname(__file__)
PHASEPY = os.path.dirname(DB)
DATA = os.path.join(PHASEPY, 'examples', 'data_20130616153750')
db_tt = os.path.join(DATA, 'tt_stations_1D.db')
db_uri = 'sqlite:///' + db_tt
engine = create_engine(db_uri)

engine_associator = create_engine(db_uri, echo=False)
BaseTT1D.metadata.create_all(engine_associator)
session = sessionmaker(bind=engine_associator)()
model = TauPyModel(model="iasp91")

for k in range(1001, 10001):
    km = k/2
    print('kilometers: ', km, kilometer2degrees(km))
    p_arrival = model.get_travel_times(source_depth_in_km=5,
                                       distance_in_degree=kilometer2degrees(km),
                                       phase_list=['P'])
    s_arrival = model.get_travel_times(source_depth_in_km=5,
                                       distance_in_degree=kilometer2degrees(km),
                                       phase_list=['S'])
    p = p_arrival[0].time
    s = s_arrival[0].time

    new_tt = TTtable1D(d_km=km,
                       delta=kilometer2degrees(km),
                       p_tt=p, s_tt=s, s_p=s-p)
    session.add(new_tt)

session.commit()
