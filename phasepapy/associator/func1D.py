from .tt_stations_1D import TTtable1D


def tt_km(session, d_km):
    """
    Look up travel time from tt_table for the closest distance to entered value
    stored in the tt_table database.
    :param session: session is the database connection
    :param d_km: float
        distance difference between the stored value returned in the lookup
        and the distance requested

    :return: TTtable_object, km_difference
    """

    minm = session.query(TTtable1D).filter(TTtable1D.d_km <= d_km).order_by(
        TTtable1D.d_km.desc()).first()

    maxm = session.query(TTtable1D).filter(TTtable1D.d_km >= d_km).order_by(
        TTtable1D.d_km).first()
    if abs(minm.d_km - d_km) <= abs(maxm.d_km - d_km):
        return minm, abs(minm.d_km - d_km)
    else:
        return maxm, abs(maxm.d_km - d_km)


def tt_s_p(session, s_p):
    """
    Look up the distance for an S-P travel time observation and return the
    closest value stored in the travel-time table

    :param session: session is the database connection
    :param s_p:
    :return: the closest tt_object, s_p_difference
    """
    minm = session.query(TTtable1D).filter(TTtable1D.s_p <= s_p).order_by(
        TTtable1D.s_p.desc()).first()

    maxm = session.query(TTtable1D).filter(TTtable1D.s_p >= s_p).order_by(
        TTtable1D.s_p).first()

    if abs(minm.s_p - s_p) <= abs(maxm.s_p - s_p):
        return minm, abs(minm.s_p - s_p)
    else:
        return maxm, abs(maxm.s_p - s_p)
