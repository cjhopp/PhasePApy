import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from phasepapy.associator.tt_stations_1D import BaseTT1D, Station1D

DB = os.path.dirname(__file__)
PHASEPY = os.path.dirname(DB)
DATA = os.path.join(PHASEPY, 'examples', 'data_20130616153750')
sc3_slqlite = os.path.join(PHASEPY, 'inv', 'inventory.sqlite')
db_tt = os.path.join(DATA, 'tt_stations_1D.db')
db_uri = 'sqlite:///' + db_tt
engine = create_engine(db_uri)

engine_associator = create_engine(db_uri, echo=False)
BaseTT1D.metadata.create_all(engine_associator)
session = sessionmaker(bind=engine_associator)()


stas = os.path.join(PHASEPY, 'db', 'ga_stations.csv')

with open(stas, 'r') as csvfile:
    csvfile.__next__()  # skip header
    reader = csv.reader(csvfile, delimiter=',')
    for ii, row in enumerate(reader):
        new_sta = Station1D(sta=row[0],
                            net=None,
                            loc=None,
                            latitude=row[1],
                            longitude=row[2],
                            elevation=row[3])
        session.add(new_sta)

session.commit()
