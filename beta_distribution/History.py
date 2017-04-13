"""
History package
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

Package for deriving a subjective logic opinion from an history of interaction
"""

from subjective_logic.Opinion import *
from BetaDistribution import *

from mpmath import *

class History():
    """
    Once initialised with the numbers of positive and negative interactions
    you will be able to call the method 
    """
    
    def get_number_of_X(self):
        return self._number_of_x
    
    def get_number_of_NotX(self):
        return self._number_of_notx
    
    def __init__(self, x, notx):
        """
        @param x: the number of positive interactions
        @param notx: the numebr of negative interactions  
        """
        self._number_of_x = x
        self._number_of_notx = notx
        self.check()

    def check(self):
        if not(
            isinstance(self._number_of_x, (int, long)) and
            isinstance(self._number_of_notx, (int, long))
            ):
                raise Exception("History is made by integers/long only!")

        if not (self._number_of_x >= 0 and self._number_of_notx >= 0):
            raise Exception("History requires an history!")

        return True
    
    def to_BetaDistribution(self):
        return BetaDistribution(self._number_of_x + 1, self._number_of_notx + 1)

    def to_Opinion(self):
        """
        @return: Subjective Logic Opinion built given the numbers of positive and negative interactions
        """
        return Opinion(mpf(self._number_of_x) / mpf(self._number_of_x + self._number_of_notx + 2),
                        mpf(self._number_of_notx) / mpf(self._number_of_x + self._number_of_notx + 2),
                        mpf(2) / mpf(self._number_of_x + self._number_of_notx + 2),
                        0.5)
    