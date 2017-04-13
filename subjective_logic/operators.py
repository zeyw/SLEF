"""
operators package
Copyright (c) 2013 Federico Cerutti <federico.cerutti@acm.org>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

DESCRIPTION:

Package encompassing the operators for subjective logic opinions
"""

from Opinion import Opinion
from config import epsilon
import mpmath

def discount(a_recommends_b, b_opinion_x):
    """
    Josang discount operator
    """
    if not (isinstance(a_recommends_b, Opinion) and isinstance(b_opinion_x, Opinion) \
            and a_recommends_b.check() and b_opinion_x.check()):
        raise Exception("Two valid Opinions are required!")

    return Opinion(
            a_recommends_b.getBelief() * b_opinion_x.getBelief(),
            a_recommends_b.getBelief() * b_opinion_x.getDisbelief(),
            a_recommends_b.getDisbelief() + a_recommends_b.getUncertainty() \
                + a_recommends_b.getBelief() * b_opinion_x.getUncertainty(),
            b_opinion_x.getBase()
            )

def consensus(a_recommends_c, b_recommends_c):
    """
    Josang consensus operator (from Trust Network Analysis with Subjective Logic -- Josang, Hayward, Pope)
    The limit case is not considered here (although is very rare due to floating point approximation)
    """
    if not (isinstance(a_recommends_c, Opinion) and isinstance(b_recommends_c, Opinion) \
            and a_recommends_c.check() and b_recommends_c.check()):
        raise Exception("Two valid Opinions are required!")

    if a_recommends_c.getUncertainty() + b_recommends_c.getUncertainty() - \
         a_recommends_c.getUncertainty() * b_recommends_c.getUncertainty() == 0:
        raise Exception("Unable to compute ")
    return Opinion(
                   (a_recommends_c.getBelief() * b_recommends_c.getUncertainty() + b_recommends_c.getBelief() * a_recommends_c.getUncertainty()) / \
                        (a_recommends_c.getUncertainty() + b_recommends_c.getUncertainty() - a_recommends_c.getUncertainty() * b_recommends_c.getUncertainty()),
                   (a_recommends_c.getDisbelief() * b_recommends_c.getUncertainty() + b_recommends_c.getDisbelief() * a_recommends_c.getUncertainty()) / \
                        (a_recommends_c.getUncertainty() + b_recommends_c.getUncertainty() - a_recommends_c.getUncertainty() * b_recommends_c.getUncertainty()),
                   (a_recommends_c.getUncertainty() * b_recommends_c.getUncertainty()) / \
                        (a_recommends_c.getUncertainty() + b_recommends_c.getUncertainty() - a_recommends_c.getUncertainty() * b_recommends_c.getUncertainty()),
                   a_recommends_c.getBase()
                   )
    
def consensus_on_a_list(list_couple_t_w):
    """
    Josang consensus operator working on a list of opinions of which we know the 
    trustworthiness degree of the source of such an opinion
    
    @param list_couple_t_w: a list of pairs <t_i, w_i> where t_i is the 
                            trustworthiness degree of the agent that tell us the
                            opinion w_i.
                            
                            In this implementation (following the Josang definition)
                            the opinions t_i are just ignored.
    """
    if not (isinstance(list_couple_t_w, (list, tuple))):
        raise Exception("List of couples of opinions <t_i, w_i> required")
    if not (len(list_couple_t_w) >= 2):
        raise Exception("Two o more couples of opinions <t_i, w_i> required")
    for a in list_couple_t_w:
        if len(a) != 2:
            raise Exception("List of couples of opinions <t_i, w_i> required")
        if not (isinstance(a[0], Opinion) and isinstance(a[1], Opinion) and \
                (a[0]).check() and (a[1]).check()):
            raise Exception("Valid opinions are required")
    
    [t,resw] = list_couple_t_w.pop(0)
    for [ti,wi] in list_couple_t_w:
        t = consensus(resw, wi)
        resw = t
    return resw

def graphical_discount_merge(list_couple_t_w):
    """
    Aberdeen geometrical operator operating on a list of opinions of which we know the 
    trustworthiness degree of the source of such an opinion
    
    @param list_couple_t_w: a list of pairs <t_i, w_i> where t_i is the 
                            trustworthiness degree of the agent that tell us the
                            opinion w_i.
    """
    if not (isinstance(list_couple_t_w, (list, tuple))):
        raise Exception("List of couples of opinions <t_i, w_i> required")
    if not (len(list_couple_t_w) >= 2):
        raise Exception("Two o more couples of opinions <t_i, w_i> required")
    for a in list_couple_t_w:
        if len(a) != 2:
            raise Exception("List of couples of opinions <t_i, w_i> required")
        if not (isinstance(a[0], Opinion) and isinstance(a[1], Opinion) and \
                (a[0]).check() and (a[1]).check()):
            raise Exception("Valid opinions are required")
    
    sumki = mpmath.mpf("0")
    belief = mpmath.mpf("0")
    disbelief = mpmath.mpf("0")
    uncertainty = mpmath.mpf("0")
    for [ti,wi] in list_couple_t_w:
        ki = ti.getBelief() + ti.getUncertainty() / 2
        sumki = sumki + ki
        belief = belief + ki * wi.getBelief()
        disbelief = disbelief + ki * wi.getDisbelief()
        uncertainty = uncertainty + ki * wi.getUncertainty()
        
    return Opinion(
                   belief / sumki,
                   disbelief / sumki,
                   uncertainty / sumki,
                   mpmath.mpf("1/2")
                   )

    

def graphical_combination(t, c):
    """
    Aberdeen graphical discount operator: original version described in http://arxiv.org/abs/1309.4994
    """
    return family_graphical_combination(t, c, ( (c.get_angle_alpha() * t.get_angle_epsilon() / (mpmath.pi / mpmath.mpf("3"))) - t.get_angle_beta()))


def graphical_combination2(t, c):
    """
    Aberdeen graphical discount operator: second version
    """
    return family_graphical_combination(t, c, (c.get_angle_alpha() * (t.get_angle_epsilon() - t.get_angle_beta()) / (mpmath.pi / mpmath.mpf("3"))))


def graphical_combination3(t, c):
    """
    Aberdeen graphical discount operator: third version
    """
    return family_graphical_combination(t, c, (c.get_angle_alpha() / (mpmath.pi / mpmath.mpf("3")) * t.get_angle_epsilon() / mpmath.mpf("2") + t.get_angle_epsilon() / mpmath.mpf("2") - t.get_angle_beta())  )
    

def family_graphical_combination(t, c, angle_alpha_prime):
    """
    Aberdeen family of graphical operators
    """
    if not (isinstance(t, Opinion) and isinstance(c, Opinion) \
            and t.check() and c.check()):
        raise Exception("Two valid Opinions are required!")

    
    if mpmath.almosteq(angle_alpha_prime, -mpmath.pi/3, epsilon):
        new_magnitude = c.get_magnitude_ratio() * (mpmath.mpf("2") * t.getUncertainty() / mpmath.sqrt(mpmath.mpf("3")))
        #new_magnitude = 0
    elif mpmath.almosteq(angle_alpha_prime, mpmath.mpf("2/3") * mpmath.pi, epsilon):
        new_magnitude = c.get_magnitude_ratio() * (mpmath.mpf("2") * (mpmath.mpf("1") - t.getUncertainty()) / mpmath.sqrt(mpmath.mpf("3")))
        #new_magnitude = 0
    elif mpmath.almosteq(angle_alpha_prime, mpmath.mpf("1/2") * mpmath.pi, epsilon):
        #new_magnitude = 1 - t.getUncertainty()
        new_magnitude = 2 * t.getBelief()
    else:
        new_magnitude = c.get_magnitude_ratio() * (mpmath.mpf("2") * \
                                                (mpmath.sqrt(mpmath.power(mpmath.tan(angle_alpha_prime), mpmath.mpf("2")) +1 ) / 
                                                 ( mpmath.absmax(mpmath.tan(angle_alpha_prime) + mpmath.sqrt(mpmath.mpf("3"))) ) ) * \
                                                t.getBelief())
      
    new_uncertainty = t.getUncertainty() + mpmath.sin(angle_alpha_prime) * new_magnitude
    new_disbelief = t.getDisbelief() + (t.getUncertainty() - new_uncertainty) * mpmath.cos(mpmath.pi/3) + mpmath.cos(angle_alpha_prime) * mpmath.sin(mpmath.pi/3) * new_magnitude
    
    if mpmath.almosteq(new_uncertainty, 1, epsilon):
        new_uncertainty = mpmath.mpf("1")
    if mpmath.almosteq(new_uncertainty, 0, epsilon):
        new_uncertainty = mpmath.mpf("0")
        
    if mpmath.almosteq(new_disbelief, 1, epsilon):
        new_disbelief = mpmath.mpf("1")
    if mpmath.almosteq(new_disbelief, 0, epsilon):
        new_disbelief = mpmath.mpf("0")
    
    
    return Opinion( 1 - new_disbelief - new_uncertainty,
                    new_disbelief,
                    new_uncertainty,
                    "1/2"
                   )
    
    
def discount_UAI_referee(t, c):
    """
    Discount operator suggested by the UAI referee
    """
    return Opinion(c.getBelief() * t.getBelief(),
                   c.getBelief() * t.getDisbelief() + c.getDisbelief(),
                   c.getBelief() * t.getUncertainty() + c.getUncertainty(),
                   "1/2"
                   )