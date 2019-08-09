"""
"""

import logging

import numpy as np
from scipy.optimize import brentq as find_root

NUMPY_TYPE = 'float64'
logger = logging.getLogger(__name__).addHandler(logger.NullHandler())

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in parameters."""
    pass

def parametrize_tir_MP(cashflows,
                       days_to_flows,
                       reference_rates,
                       day_count_base=365):
    """
    Return the function for a net present value using discount rates combined from reference rates and a spread as the only variable for a set of time-determined cashflows.
    
    Defines a function using a particular trick found at stackoverflow__
    
    __
    .. _stackoverflow:
    http://stackoverflow.com/questions/233673/lexical-closures-in-python/235764#235764

    Keyword arguments:
    - `cashflows`: money-value of future cashflows (list)
    - `days_to_flows`: number of days till the cashflows are due (list)
      len(day_to_flows) == len(cashflows)
    - `reference_rates`: reference rate for cashflows as "efectiva anual" (list)
      len(reference_rates) == len(cashflows) or len(reference_rates) == 1
    - `day_count_base`: day count base
      default = 365 (as required by "Circular Externa 030 de 2009")
      
    """
    
    # Check inputs
    if len(cashflows) != len(days_to_flows):
        raise InputError(expr = "Error in parametrize_tir_MP(), len(cashflows) must be equal to len(day_to_flows)")
    elif len(cashflows) != len(reference_rates) and len(reference_rates) != 1:
        raise InputError(expr = "Error in parametrize_tir_MP(), len(reference_rates) must equal to len(cashflows) or equal to 1")
    
    if len(reference_rates) == 1:
        reference_rates = reference_rates * len(cashflows) # repetition of list reference_rates
    
    # Log
    logger.debug('Paremetrizando funcion de margen propio con:\n')
    logger.debug('{0:>26} {1:>26} {2:>26}'.format('Flujo', 'Dias flujo', 'Tasa_referencia'))
    
    for flow, days, rate in zip(cashflows, days_to_flows, reference_rates):
        logger.debug('{0:>26} {1:>26} {2:>26}'.format(flow, days, rate))
    
    # Convert inputs to numpy arrays
    cashflows = np.array(cashflows, dtype=NUMPY_TYPE)
    days_to_flows = np.array(days_to_flows, dtype=NUMPY_TYPE)
    reference_rates = np.array(reference_rates, dtype=NUMPY_TYPE)
    
    # Define parametrized function
    def func(spread):
        """
        Dynamically defined function
        
        Net present value using discount rates combined from reference rates and a MP for a set of time-determined cashflows in the future.
        """        
        pvs = cashflows/(((1+reference_rates)*(1+spread))**(days_to_flows/day_count_base))
        
        # Return parametrized function
        return np.sum(pvs) 
            
    return func


def parametrize_tir(cashflows,
                       days_to_flows,
                       day_count_base=365):
    """
    Return the function for a net present value with a discount rate as the only variable for a set of time-determined cashflows.
    
    Defines a function using a particular trick found at stackoverflow__
    
    __
    .. _stackoverflow:
    http://stackoverflow.com/questions/233673/lexical-closures-in-python/235764#235764

    Keyword arguments:
    - `cashflows`: money-value of future cashflows (list)
    - `days_to_flows`: number of days till the cashflows are due (list)
      len(day_to_flows) == len(cashflows)
    - `day_count_base`: day count base
      default = 365 (as required by "Circular Externa 030 de 2009")
      
    """
    
    # Check inputs
    if len(cashflows) != len(days_to_flows):
        error_string = "Error in parametrize_tir_MP, len(cashflows) must be equal to len(day_to_flows)"
        logger.error(error_string)
        raise InputError(expr = error_string)
    
    # Log
    logger.debug('Paremetrizando funcion de margen propio con:\n')
    logger.debug('{0:>26} {1:>26}'.format('Flujo', 'Dias flujo'))
    
    for flow, days in zip(cashflows, days_to_flows):
        logger.debug('{0:>26} {1:>26}'.format(flow, days))
    
    # Convert inputs to numpy arrays
    cashflows = np.array(cashflows, dtype=NUMPY_TYPE)
    days_to_flows = np.array(days_to_flows, dtype=NUMPY_TYPE)
    
    # Define parametrized function
    def func(spread):
        """
        Dynamically defined function
        
        Net present value using discount rates combined from reference rates and a MP for a set of time-determined cashflows in the future.
        """        
        pvs = cashflows/((1+spread)**(days_to_flows/day_count_base))
        
        # Return parametrized function
        return np.sum(pvs) 
            
    return func


if __name__ == '__main__':
    rate = 0.052
    flow_list = [-1003000,5000,5000,5000,5000,1000000]
    days_list = [0,28,118,208,298,298]
    reference_rate = [rate]
    
    npv_MP = parametrize_tir_MP(flow_list,
                             days_list,
                             reference_rate)
    
    npv_TIR = parametrize_tir(flow_list,
                             days_list)
    
    print(find_root(npv_MP,-0.999,0.999))
    print(find_root(npv_TIR,-0.999,0.999))
    
    
