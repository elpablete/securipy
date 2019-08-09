"""
"""

from __future__ import division
import logging

logger = logging.getLogger(__name__).addHandler(logger.NullHandler())

class InterestRate(object):
    """Base class for interest rates.
    
    """
    def __init__(self, i, piy, add_method=None, term='EMR1'):
        """Create an interest rate.
        
        :i: value of the interest rate stated as a fraction (**not** percentage).
        :piy: number of periods in a year for the rate expressed in natural terms
        :term: string representing the term of the interest rate
        """
        self.i = i
        self.term = term
        self.piy = piy
        self.add_method = add_method
        if add_method is None:
            self.add_spread = None
        elif add_method == 'add':
            self.add_spread = self._add
        elif add_method == 'combine':
            self.add_spread = self._combine
        else:
            #raise InputError(expr='Parameter add_spread is not valid')
            pass
    
    def _combine(self, spread):
        """Combine the rate value with the spread and return an interestRate.
        
        :spread: spread to combine with the rate.
        
        Uses the formula:
        c_r = (1+i_r) * (1+spread) - 1
        """
        #aer_rate = self.to_AER()
        combined_rate = (1+self.to_AER())*(1+spread)-1
        return InterestRate(combined_rate, self.piy, self.term)
    
    def _add(self, spread):
        """Add the rate value with the spread and return an interestRate.
        
        :spread: spread to add to the rate.
        
        """
        return InterestRate(self.i + spread, self.piy, self.term)
    
    def to_AER(self):
        """Convert to Annual Effective Interest Rate.
        """
        return change_rate(self.i, self.term, self.piy)
    
    def __repr__(self):
        return "interestRate(i=%(i)r, piy=%(piy)r, add_method=%(add_method)r, term=%(term)r)" % {'i':self.i, 'piy':self.piy, 'add_method':self.add_method, 'term':self.term}
    

def _change_eff(i_rate1, piy1, piy2):
    """Convert rate expressed in terms of one effectivity to a different one.
    
    Change interest rate in terms of p1 periods in a year to a rate in terms of p2 periods in a year.
    
    :i_rate1: initial interest rate to be changed.
    :piy1: number of periods in a year for `i_rate1`
    :piy1: number of period in a year for the desired interest rate
    
    Uses this equivalence:
    
                 piy1                piy2
    (1 + i_rate1)     = (1 + i_rate2)
    """
    
    return (1 + i_rate1)**(piy1/piy2) - 1

def _nom_2_eff(nominal_rate, piy):
    """Convert a nominal rate to an effective rate.
    
    :nominal_rate: nominal rate to be changed
    :piy: number of periods in a year for the nominal rate
    """
    return nominal_rate / piy

def _eff_2_nom(effective_rate, piy):
    """Convert an effective rate to a nominal rate.
    
    :effective_rate: effective rate to be changed
    :piy: number of periods in a year for the effective rate
    """
    return effective_rate * piy

def _mat_2_ant(matured_rate):
    """Convert an matured rate to its anticipated term.
    
    :matured_rate: matured rate to be converted
    
    Uses the following equivalence:
    
                              matured_rate
      anticipated_rate =  --------------------
                          ( 1 + matured_rate )
    """
    return matured_rate/(1+matured_rate)

def _ant_2_mat(anticipated_rate):
    """Convert an anticipated rate to its matured term.
    
    :anticipated_rate: anticipated rate to be converted
    
    Uses the following equivalence:
    
                          anticipated_rate
      matured_rate =  ------------------------
                      ( 1 - anticipated_rate )
    """
    return anticipated_rate/(1-anticipated_rate)


def change_rate(i_rate, i_case, piy1, f_case='EMR2', piy2=1):
    """Convert rate to equivalent one.
    
    Change a rate using the rate equivalence chart from `Guillermo Baca Currea`[Baca2005]
    
    :i_rate: initial rate to be changed
    :i_case: code for initial case
    :f_case: code for the desired final case
    :piy1: number of periods in a year for the initial rate
    :piy2: number of periods in a year for the desired rate
    
    Allowed values for cases:
     'ANR1', 'AER1', 'EMR1', 'MNR1', 'ANR2', 'AER2', 'EMR2', 'MNR2'
    
    
                             *PIY1* || *PIY2*
    (ANR) --> (AER)                 ||                 (AER) --> (ANR)
                   \                ||                /
                    '--> (EMR) -----++----> (EMR) ---'
                   /                ||                \
         (MNR) ---'                 ||                 '--> (MNR)
                                    ||
    
    
    ANR : 
        Anticipated Nominal Rate
        
    AER : 
        Anticipated Matured Rate
        
    EMR :
        Effective Matured Rate
        
    MNR : 
        Matured Nominal Rate
    """
    log = 'Changing %(i_rate)f[%(i_case)s], with %(piy1)f period in a year' % {"i_rate": i_rate, "i_case": i_case, "piy1": piy1}
    logger.debug(log)
    log = 'to a [%(f_case)s] with %(piy2)f periods in a year.' % {"f_case": f_case, "piy2": piy2}
    logger.debug(log)
    
    case_list = ['ANR1', 'AER1', 'EMR1', 'MNR1',
                 'ANR2', 'AER2', 'EMR2', 'MNR2']
    
    case = i_case
    f_rate = i_rate
    while case != f_case:
        case1 = case
        rate1 = f_rate
        if case == 'MNR1':
            #Matured Nominal --> Effective Matured
            f_rate = _nom_2_eff(f_rate, piy1)
            case = 'EMR1'
        elif case == 'EMR1':
            #Effective Matured --> Effective Matured
            f_rate = _change_eff(f_rate, piy1, piy2)
            case = 'EMR2'
        elif case == 'EMR2':
            #Branch
            if f_case == 'AER2' or f_case == 'ANR2':
                #Effective Matured --> Anticipated Effective
                f_rate = _mat_2_ant(f_rate)
                case = 'AER2'
            elif f_case == 'MNR2':
                #Effective Matured --> Matured Nominal
                f_rate = _eff_2_nom(f_rate, piy2)
                case = 'MNR2'
            else:
                #raise Error(expr= "")
                pass
        elif case == 'MNR2':
            #Matured Nominal
            pass
        elif case == 'ANR1':
            #Anticipated Nominal --> Anticipated Effective
            f_rate = _nom_2_eff(f_rate,piy1)
            case = 'AER1'
        elif case == 'AER1':
            #Anticipated Effective --> Effective Matured
            f_rate = _ant_2_mat(f_rate)
            case = 'EMR1'
        elif case == 'AER2':
            #Anticipated Effective --> Anticipated Nominal
            f_rate = _eff_2_nom(f_rate, piy2)
            case = 'ANR2'
        elif case == 'ANR2':
            #Anticipated Nominal
            pass
        else:
            #raise InputError(expr = "")
            pass
        case2 = case
        rate2 = f_rate
        log = '%(r1)f[%(c1)s]->%(r2)f[%(c2)s]' % {"c1":case1, "r1": rate1, "c2":case2, "r2":rate2}
        logger.debug(log)

    return f_rate
    
    
if __name__ == '__main__':
    IBR1 = InterestRate(3.2/100, 360/28, 'add', 'MNR1')
    IBR = InterestRate(3.2/100, 12, 'add', 'MNR1')
    spread = 2/100
    IBR_combine = IBR.add_spread(spread)
    IBR_add = IBR.add_spread(spread).to_AER()
    print(((((3.2/100) + (2/100))/12)+1)**(12)-1)
    print(IBR_add)
    print(IBR_combine.i)
    print(IBR)
    print(InterestRate(0.09,32))
    #print ((((3.2/100) + (2/100))/(360/28))+1)**(360/28)-1
    #change_rate(rate1, icase, piy1, fcase, piy2)

