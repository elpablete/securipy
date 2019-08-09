"""
"""
from __future__ import division

import logging

from datetime import date
from datetime import timedelta
import math

logger = logging.getLogger(__name__).addHandler(logger.NullHandler())

def _isleap(year):
    """Return True for leap years and False otherwise.
    """
    return year % 4 == 0 and (year % 100 !=0 or year % 400 == 0)

def _is_end_of_month(date):
    """Checks if date is an end of the month.
    """
    return date == end_of_month(date)
    
def end_of_month(date):
    """Return a datetime.date object as the end of the month of date.month 
    """ 
    end_of_month = {1:31,
                    2:None,
                    3:31,
                    4:30,
                    5:31,
                    6:30,
                    7:31,
                    8:31,
                    9:30,
                    10:31,
                    11:30,
                    12:31}
    if not date.month == 2:
        return date.replace(day=end_of_month[date.month])
    elif _isleap(date.year):
        return date.replace(day=29)
    else:
        return date.replace(day=28)
    
def _days_in_leap_and_common_years(i_date, f_date):
    """Return the a tuple with number of days in common and leap years (respectively) between initial and final dates.
    """
    
    iy = i_date.year
    fy = f_date.year
    
    days_in_leap = 0
    days_in_common = 0
    if iy == fy:
        # same year
        delta = f_date - i_date
        if _isleap(iy):
            days_in_leap += delta.days
        else:
            days_in_common += delta.days
    elif fy - iy >= 1:
        # different year
        delta1 = i_date.replace(year = iy+1, month=1, day=1) - i_date # days in initial year
        delta2 = f_date - f_date.replace(month=1, day=1) # days in final year
        
        if _isleap(iy):
            days_in_leap += delta1.days
        else:
            days_in_common += delta1.days
        
        if _isleap(fy):
            days_in_leap += delta2.days
        else:
            days_in_common += delta2.days
        
        leaps_in_between = [y for y in range(iy+1, fy) if _isleap(y)]
        commons_in_between = [y for y in range(iy+1, fy) if not(_isleap(y))]
        
        days_in_leap += len(leaps_in_between) * 366
        days_in_common += len(commons_in_between) * 365
    #else:
        #raise InputError(expr = "Error in days_in_years(), f_date.year must be greater than i_date.year")
        
    return (days_in_leap, days_in_common)
    
def periodic_date_gen(start_date, end_date, periodicity_in_months):
    """Generates periodic dates
    
    
    """
    """tdelta = end_date - start_date
    n_dates = int(math.ceil(tdelta.total_seconds() / (2629743.83 * periodicity_in_months)))
    print range(n_dates + 1)
    dates = [edate(end_date, -i*periodicity_in_months) for i in range(n_dates + 1)]
    print dates[::-1]
    """
    
    l_date = end_date
    dates =[l_date]
    date_count = 1
    while l_date > start_date:
        l_date = edate(end_date, -date_count*periodicity_in_months)
        dates.append(l_date)
        date_count += 1
    return dates[::-1]

def edate(d, months):
    """Same date nth months away, 'alla Excel'.
    
    :d: a datetime.date instance from the datetime module
    """
    new_month = ((( d.month - 1) + months ) % 12 ) + 1
    new_year  = d.year + ((( d.month - 1) + months ) // 12 )
    try:
        return date(new_year, new_month, d.day)
    except ValueError:
        return end_of_month(date(new_year, new_month, 1))

if __name__ == '__main__':
    
    date1 = date(2012, 2, 5)
    date2 = date(2012, 4, 6)

    print(_isleap(date1.year))
    print(_is_end_of_month(date1))
    print(_days_in_leap_and_common_years(date1, date2))
    
    date1 = date(2012, 1, 30)
    date2 = date(2012, 1, 30)
    print(edate(date1, +1))
    print(edate(date2, -1))
    print(edate(date1, 0))
    
    print("*************************************************")
    print("edate check")
    for day_delta in range(0,1):
        for month_delta in range(-3, 4, 1):
            the_date = date1 + timedelta(days=day_delta)
            the_edate = edate(the_date, month_delta)
            print("base date: %(bdate)s; months: %(months)s; edate: %(edate)s" % {'bdate': the_date, 'months': month_delta, 'edate': the_edate})
    
    print("*************************************************")
    
    date3 = date(2012, 1, 31)
    date4 = date(2014, 1, 31)
    
    for d in periodic_date_gen(date3, date4, 3):
        print(d.__str__())
    