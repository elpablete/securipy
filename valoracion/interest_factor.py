"""
"""
from __future__ import division
from datetime import date
import logging
from date_helper import *

logger = logging.getLogger(__name__).addHandler(logger.NullHandler())

def check_date_objects(date1, date2):
    if not(isinstance(date1, date) or isinstance(date2, date)):
        raise InputError(expr = "Dates must be instances of datetime.date class")

class Error(Exception):
    """Base class for exceptions in this module.
    """
    pass

class InputError(Error):
    """Exception raised for errors in parameters.
    """
    pass



def _days_30_360_main(i_year, i_month, i_day, f_year, f_month, f_day):
    """Base formula calculation for the numerator and denominator of day count 30/360.
    """
    num = 360 * (f_year - i_year) + 30 * (f_month - i_month) + (f_day - i_day)
    den = 360
    log = "[%(num)r/%(den)r]" % {'num':num, 'den':den}
    logger.debug(log)
    return num / den
        

def _daycount_act_act_ISDA(i_date, f_date):
    """Return factor to apply for interests between i_date and f_date.
    
    :i_date: initial date.
    :f_date: final date.
    
    *i_date* and *f_date* must be instances of datetime.date class from datetime module
    
    act/act, ISDA
    Days in a month: actual
    Days in a year: actual
    Flavor: ISDA
    
    This method splits up the actual number of days falling in leap years and in non-leap years.
    The year fraction is the sum of the actual number of days falling in leap years divided by 366 and the actual number of days falling in non-leap years divided by 365.
    """
    days_in_commons, days_in_leaps = _days_in_leap_and_common_years(i_date, f_date)
    
    if days_in_commons == 0:
        num = days_in_leaps
        den = 366
    elif days_in_leaps == 0:
        num = days_in_commons
        den = 365
    else:
        num = (366 * days_in_commons) + (365 * days_in_leaps)        
        den = 133590 #least common multiple between 366 and 365
    
    log = "%(f_name)r(%(i_date)r, %(f_date)r)" % {'f_name':'daycount_act_act_ISDA', 'i_date':i_date, 'f_date':f_date}
    logger.debug(log)
    log = "[%(num)r/%(den)r]" % {'num':num, 'den':den}
    logger.debug(log)
    return num / den

def _daycount_act_act_Euro(i_date, f_date):
    """Return factor to apply for interests between i_date and f_date.
    
    :i_date: initial date.
    :f_date: final date.
    
    *i_date* and *f_date* must be instances of datetime.date class from the datetime module
    
    act/act, Euro, AFB
    Days in a month: actual
    Days in a year: actual
    
    This method first calculates the number of full years counting backwards from the second date.
    For any resulting stub periods, the numerator is the actual number of days in the period, the denominator being 365 or 366 depending on whether February 29th falls in the stub period.
    """
#    delta = f_date - i_date
#    days1 = delta.days
#    
#    log = "%(f_name)r(%(i_date)r, %(f_date)r)" % {'f_name':'daycount_act_act_Euro', 'i_date':i_date, 'f_date':f_date}
#    logger.debug(log)
#    log = "[%(num)r/%(den)r]" % {'num':num, 'den':den}
#    logger.debug(log)
#    return num / den

def _daycount_act_365_Fixed(i_date, f_date):
    """Return factor to apply for interests between i_date and f_date.
    
    :i_date: initial date.
    :f_date: final date.
    
    *i_date* and *f_date* must be instances of datetime.date class from the datetime module
    
    act/365, act/365 fixed
    Days in a month: actual
    Days in a year: 365 Always
    Flavor: Fixed
    
    This method first calculates the number of full years counting backwards from the second date.
    For any resulting stub periods, the numerator is the actual number of days in the period, the denominator being 365 or 366 depending on whether February 29th falls in the stub period.
    """
    delta = f_date - i_date
    num = delta.days
    den = 365
    
    log = "%(f_name)r(%(i_date)r, %(f_date)r)" % {'f_name':'daycount_act_365_Fixed', 'i_date':i_date, 'f_date':f_date}
    logger.debug(log)
    log = "[%(num)r/%(den)r]" % {'num':num, 'den':den}
    logger.debug(log)
    return num / den

def _daycount_30_360(i_date, f_date):
    """Return factor to apply for interests between i_date and f_date.
    
    :i_date: initial date.
    :f_date: final date.
    
    *i_date* and *f_date* must be instances of datetime.date class from the datetime module
    
    Days in a month: 30
    Days in a year: 360
    Flavor: None
    """
    i_year = i_date.year
    i_month = i_date.month
    i_day = i_date.day
    
    f_year = f_date.year
    f_month = f_date.month
    f_day = f_date.day
    
    log = "%(f_name)r(%(i_date)r, %(f_date)r)" % {'f_name':'daycount_30_360', 'i_date':i_date, 'f_date':f_date}
    logger.debug(log)
    factor = _days_30_360_main(i_year, i_month, i_day, f_year, f_month, f_day)
    return factor

def _daycount_30_360_US(i_date, f_date):
    """Return factor to apply for interests between i_date and f_date.
    
    :i_date: initial date.
    :f_date: final date.
    
    *i_date* and *f_date* must be instances of datetime.date class from the datetime module
    
    Days in a month: 30
    Days in a year: 360
    Flavor: US
    """
    i_year = i_date.year
    i_month = i_date.month
    i_day = i_date.day
    
    f_year = f_date.year
    f_month = f_date.month
    f_day = f_date.day
    
    
    if (i_date.month == 2 and _is_end_of_month(i_date)) and (f_date.month == 2 and _is_end_of_month(f_date)):
        f_day = 30
    if (i_date.month == 2 and _is_end_of_month(i_date)):
        i_day = 30
    if (f_day == 31) and (i_day in [30, 31]):
        f_day = 30
    if  (i_day == 31):
        i_day = 30
    
    log = "%(f_name)r(%(i_date)r, %(f_date)r)" % {'f_name':'daycount_30_360_US', 'i_date':i_date, 'f_date':f_date}
    logger.debug(log)
    factor = _days_30_360_main(i_year, i_month, i_day, f_year, f_month, f_day)
    return factor

class InterestFactor(object):
    """.
    
    Usage::
    >>> date1 = date(2012, 2, 5)
    >>> date2 = date(2012, 4, 6)
    >>> myCounter = DayCounter(30, 360, 'fixed')
    >>> myCounter.count(date1, date2)
    >>> 
    
    """

    def __init__(self, dim=30, diy=360, flavor=None):
        """Constructor.
        
        """
        self.dim = dim
        self.diy = diy
        self.flavor = flavor
        
        method = '_'.join([str(self.dim), str(self.diy), str(self.flavor)])
        #try:
        self.factor = self._methods[method]
        #except KeyError as e:
            #pass #TODO: catch this key error
        
    def __repr__(self):
        """Representation.
        
        """
        return "interestFactor(dim=%(dim)r, diy=%(diy)r, flavor=%(flavor)r)" % {'dim':self.dim, 'diy':self.diy, 'flavor':self.flavor}
    
    _methods = {
                 '30_360_None':     _daycount_30_360,
                 '30_360_US':       _daycount_30_360_US,
                 'act_act_Fixed':   _daycount_act_365_Fixed,
                 'act_act_ISDA':    _daycount_act_act_ISDA,
                 'act_act_Euro':    _daycount_act_act_Euro,
                 }
    

if __name__ == '__main__':
    
    date1 = date(2012, 2, 5)
    date2 = date(2012, 4, 6)
    days360 = InterestFactor(30, 360)
    print(days360)
    print(days360.factor(date1, date2))
    
