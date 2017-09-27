from obspy import read as obspy_read


def test_picker_integration(event, picker):
    mseed = event + '_short.mseed'
    st = obspy_read(mseed)
    total_picks = []
    for s in st[:2]:
        _, picks, _, _, _ = picker().picks(s)
        total_picks += picks

    assert len(total_picks)
