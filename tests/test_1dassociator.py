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


FILEPATH = os.path.dirname(__file__)
PHASEPAPY = os.path.dirname(FILEPATH)
EX_DATA = os.path.join(PHASEPAPY, 'examples', 'data_20130616153750')

palog.configure('DEBUG')
log = logging.getLogger(__name__)
db_tt = os.path.join(EX_DATA, 'tt_stations_1D.db')


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
    picker = fbpicker.FBPicker(t_long=5, freqmin=0.5, mode='rms', t_ma=20,
                               nsigma=3,
                               t_up=0.78, nr_len=2, nr_coeff=2, pol_len=10,
                               pol_coeff=10, uncert_coeff=3)

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
    # Add singles stations to events
    assocOK.single_phase()

    events = assocOK.assoc_db.query(Associated).all()
    assert len(events) == 1
    event = events[0]
    assert event.nsta == 3
    print(event.longitude, event.latitude)
    assert abs(event.longitude + 137.993) < 1.0e-3
    assert abs(event.latitude - 68.786) < 1.0e-3
