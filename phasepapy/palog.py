import logging


def configure(verbosity):
    log = logging.getLogger("")
    log.setLevel(verbosity)
    ch = logging.StreamHandler()
    formatter = ElapsedFormatter()
    ch.setFormatter(formatter)
    log.addHandler(ch)


class ElapsedFormatter:

    def format(self, record):
        lineno = record.lineno
        lvl = record.levelname
        name = record.name
        t = int(round(record.relativeCreated/1000.0))
        msg = record.getMessage()
        logstr = "+{}s {}:{}: {} {}".format(t, name, lineno, lvl, msg)
        return logstr