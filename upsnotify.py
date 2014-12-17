#!/home/entone/Envs/clubhouse/bin/python
try:
    import os
    import sys
    import logging
    import logging.handlers
    
    my_logger = logging.getLogger(__name__)
    my_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    my_logger.addHandler(handler)
    my_logger.debug("TEST!")

    from lib.PyNUT import PyNUTClient
    my_logger.debug(PyNUTClient)    
    from model import TimeSeriesMetric
    my_logger.debug(TimeSeriesMetric)

    _pnut = PyNUTClient(login='clubhouse', password='abudabu1', debug=True)
    my_logger.debug(_pnut)


    prog = sys.argv[0]
    m_type = os.environ.get('NOTIFYTYPE').lower()
    message = sys.argv[1].split("@")[0].replace(" ", "-").lower().split("-")[1]

    my_logger.debug("PROGRAM: {}".format(prog))
    my_logger.debug("MESSAGE: {}".format(message))
    my_logger.debug("NOTIFYTYPE: {}".format(m_type))

    reason = _pnut.GetUPSVars(message).get('input.transfer.reason', "")

    my_logger.debug("REASON: {}".format(reason))
    _type = "{}-{}".format(message, m_type)
    my_logger.debug("TYPE: {}".format(_type))
    tm = TimeSeriesMetric(_type, reason).save()
except Exception as e:
    my_logger.exception(e)