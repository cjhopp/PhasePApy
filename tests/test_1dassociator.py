import os
import shutil
import logging
import glob
from obspy.core import read as obspy_read, Stream
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from phasepapy import palog
from phasepapy.phasepicker import fbpicker
from phasepapy.associator import tables1D, assoc1D
from phasepapy.associator.tables1D import Associated
from phasepapy.associator.assoc1D import locating
from phasepapy.associator.assoc1D import outlier_cutoff
from phasepapy.associator.assoc1D import residuals_minimum
from phasepapy.associator.assoc1D import datetime_statistics
from scipy.optimize import fmin

import pytest

FILEPATH = os.path.dirname(__file__)
print ('FILEPATH   = ',FILEPATH)
PHASEPAPY = os.path.dirname(FILEPATH)
print ('PHASEPAAPY = ',PHASEPAPY)
EX_DATA = os.path.join(PHASEPAPY, 'examples', 'data_20130616153750')

palog.configure('DEBUG')
log = logging.getLogger(__name__)
db_tt = os.path.join(EX_DATA, 'tt_stations_1D.db')
# enabling and disabling log
log.disabled = True

def test_1dassociater(random_filename):
    db_assoc = random_filename(ext='.db')
    db_tt_test = random_filename(ext='.db')

    # Our SQLite databases are:
    db_assoc = 'sqlite:///' + db_assoc
    shutil.copy(db_tt, db_tt_test)
    db_tt_test = 'sqlite:///' + db_tt_test
    # Traveltime database
    # Connect to our databases
    engine_assoc = create_engine(db_assoc, echo=False)
    # # Create the tables required to run the 1D associator
    tables1D.Base.metadata.create_all(engine_assoc)
    Session = sessionmaker(bind=engine_assoc)
    session = Session()
    # Find all waveform data in the data directory
    file_list = glob.glob(os.path.join(EX_DATA, '*.msd'))

    # Define our picker instance
    picker = fbpicker.FBPicker(
		t_long=5,   freqmin=0.5 ,     mode='rms',     t_ma=20,
                nsigma=3,      t_up=0.78,       nr_len=2,  nr_coeff=2, 
                pol_len=10, pol_coeff=10, uncert_coeff=3)

    st = Stream()

    for f in file_list:
        st += obspy_read(f)

    # Pick the waveforms
    for s in st:
        # st.merge()  # merge will cause issues if there is a data gap
        s.detrend('linear')
        scnl, picks, polarity, snr, uncert = picker.picks(s)
        t_create = datetime.utcnow()  # Record the time we made the picks
        # Add each pick to the database
        for i in range(len(picks)):
            log.debug('st = {} Pick = {} {} {} scnl = {}'.format(s,i,picks[i],picks[i].datetime,scnl))
            
            new_pick = tables1D.Pick(scnl, picks[i].datetime, polarity[i],
                                     snr[i], uncert[i], t_create)
            session.add(new_pick)  # Add pick i to the database
        session.commit()  # Commit the pick to the database
        log.debug('Wrote picks')

    # Define the associator
    assocOK = assoc1D.LocalAssociator(db_assoc, db_tt_test,
                                      max_km=350,
                                      aggregation=1,
                                      aggr_norm='L2',
                                      cutoff_outlier=30,
                                      assoc_ot_uncert=7,
                                      nsta_declare=3,
                                      loc_uncert_thresh=0.2)
    # Identify candidate events (Pick Aggregation)
    assocOK.id_candidate_events()
    # Associate events
    assocOK.associate_candidates()

    print ("Unit Testing for 1Dassociator ...............")


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #   Function Testing rms sort list
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    radius = [
                ('SIO', -137.26, 68.992, 83.5, 0.7514, 0), 
                ('U32A', -137.26, 68.992, 203.0, 1.8268, 1), 
                ('W35A', -137.26, 68.992, 42.5, 0.3825, 2), 
                ('OKCFA', -137.26, 68.992, 33.0, 0.297, 3), 
                ('X34A', -137.26, 68.992, 122.0, 1.0979, 4), 
                ('FNO', -137.26, 68.992, 36.5, 0.3285, 5),
              ]
    lon = -137.26; lat = 68.992
    st_declare = 3 # number of station requires to monitor earth quake
    rms_sort=[]
    rms_sort,cb = assocOK._LocalAssociator__accumulate_rms_sort(radius, lon, lat, st_declare)
        
    print ("")
    print ('rms                   = {}'.format(rms_sort))
    print ('Combinations Stations = {}'.format(cb))
    print ("")
    assert len(rms_sort) > 0

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #   Function Testing for radius paremeters 
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#    candis_arr = [Candidate Event <2013-06-16T15:38:50.150000 U32A 203.00 1.83 18 19>]
#    radius=[]
#    radius, lon, lat = assocOK.accumulate_radius(candis_arr)
#    print ("")
#    print ("Radius    = {}".format(radius))
#    print ("Lon       = {}".format(lon))
#    print ("Lat       = {}".format(lat))


    # Add singles stations to events
    assocOK.single_phase()

    events = assocOK.assoc_db.query(Associated).all()
    assert len(events) == 1
    event = events[0]
    assert event.nsta == 3
    print ('event.longitude = ',event.longitude )
#    assert abs(event.longitude + 137.596) < 1.0e-3
    print ('event.latitude = ',event.latitude )
#    assert abs(event.latitude + ) < 1.0e-3


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# test for fmin ( Simplex Algorithm )
# Simplex algorithm is probably the simplest way to minimize 
# a fairly well behaved function.  It does not use gradient 
# evaluations, it takes longer to find minimum.
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize (
     "radius_cb, lon, lat",
     [ 
        ((('SIO', -137.26, 68.992, 83.5, 0.7514, 0),
         ('U32A', -137.26, 68.992, 203.0, 1.8268, 1),
         ('W35A', -137.26, 68.992, 42.5, 0.3825, 2),
         ('OKCFA', -137.26, 68.992, 33.0, 0.297, 3),
         ('X34A', -137.26, 68.992, 122.0, 1.0979, 4),
         ('FNO', -137.26, 68.992, 36.5, 0.3285, 5)),
          -137.26, 68.992),
      ]
)

def test_fmin(radius_cb,lon, lat):
    location = fmin(locating, [lon, lat], radius_cb,disp=0)
    print (' seperate test location = {}', location)
    assert abs(location[0]) > 0
    assert abs(location[1]) > 0



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#   Function for Testing outer cutoff 
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize (
     "matches, location,cutoff_outer",
     [
           ((('SIO', -137.26, 68.992, 83.5, 0.7514, 0),
            ('U32A', -137.26, 68.992, 203.0, 1.8268, 1),
            ('W35A', -137.26, 68.992, 42.5, 0.3825, 2),
            ('OKCFA', -137.26, 68.992, 33.0, 0.297, 3),
            ('X34A', -137.26, 68.992, 122.0, 1.0979, 4),
            ('FNO', -137.26, 68.992, 36.5, 0.3285, 5)),
            [-137.26, 68.992],
            30 ),
     ]
)

def test_outlier_cutoff(matches,location, cutoff_outer):
    matches, mismatches = outlier_cutoff(matches, location, cutoff_outer)
    print ("")
    print ("matches    = {}".format(matches))
    print ("mismatches = {}".format(mismatches))
    assert len(matches) > 0    


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#   Function for Testing minimu residulas 
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize (
     "location,args",
     [
            ([-137.26, 68.992],
            (('SIO', -137.26, 68.992, 83.5, 0.7514, 0),
            ('U32A', -137.26, 68.992, 203.0, 1.8268, 1),
            ('W35A', -137.26, 68.992, 42.5, 0.3825, 2),
            ('OKCFA', -137.26, 68.992, 33.0, 0.297, 3),
            ('X34A', -137.26, 68.992, 122.0, 1.0979, 4),
            ('FNO', -137.26, 68.992, 36.5, 0.3285, 5))
           ),
     ]
)

def test_residual_minimum(location, args):
    min_residual = residuals_minimum(location, args)
    print ("")
    print ("min_residual    = {}".format(min_residual))
    assert abs(min_residual) > 0    



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#   date time statistics
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize (
     "cluster_time",
     [
         [datetime(2013, 6, 16, 15, 39, 10, 800000), 
          datetime(2013, 6, 16, 15, 39, 10, 870000)]
     ]
)
def test_datetime_statistics(cluster_time):
    pickave, pickstd = datetime_statistics(cluster_time)
    print ("")
    print ("pickave   = {}".format(pickave))
    print ("pickstd   = {}".format(pickstd))
    assert pickstd >= 0
