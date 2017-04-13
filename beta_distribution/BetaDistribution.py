"""
BetaDistribution package
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

Package for creating a beta distribution
"""

import math
from NotABetaDistributionException import *

import scipy.special
import numpy
import pylab

class BetaDistribution():

    def getAlpha(self):
        return self._alpha
    
    def getBeta(self):
        return self._beta

    
    def __init__(self, alpha, beta):
        self._alpha = alpha
        self._beta = beta
        self.check()


    def check(self):
        if not(self._alpha > 0 and self._beta > 0):
            raise NotABetaDistributionException(self)

    def __repr__(self):
        return "BetaDistribution("+repr(self._alpha)+","+repr(self._beta)+")"


    def distribution(self, p):
        if not(p >= 0 and p <= 1):
            raise Exception("Distributions are computed between 0 and 1...")

        if (p == 0 and self._alpha < 1):
            return 0
        if (p == 1 and self._beta < 1):
            return 0

        return 1 / scipy.special.beta(self._alpha, self._beta)* \
                math.pow(p, (self._alpha - 1)) * math.pow((1 - p), (self._beta - 1))


    def plotdistribution(self):
        p = numpy.arange(0.0, 1.0, 0.01)
        r = []
        for a in numpy.nditer(p):
            r.append(self.distribution(a))

        pylab.plot(p, r)
        pylab.show()