"""
an unittest package
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
"""

import unittest

from beta_distribution.BetaDistribution import *
from beta_distribution.NotABetaDistributionException import *

class  BetadistributionTestCase(unittest.TestCase):

    def setUp(self):
        self.b = BetaDistribution(1, 1)
        self.alphalessthan1 = BetaDistribution(0.5, 1)
        self.betalessthan1 = BetaDistribution(1, 0.5)

    def test_betadistribution_input1(self):
        self.assertRaises(NotABetaDistributionException, BetaDistribution, 0, 0)

    def test_betadistribution_input2(self):
        self.assertRaises(NotABetaDistributionException, BetaDistribution, -0.5, 0)

    def test_betadistribution_input3(self):
        self.assertRaises(NotABetaDistributionException, BetaDistribution, 0, -0.3)

    def test_betadistribution_input4(self):
        self.assertRaises(NotABetaDistributionException, BetaDistribution, -0.5, -0.3)

    def test_betadistribution_distribution1(self):
        self.assertRaisesRegexp(Exception, "Distributions are computed between 0 and 1...", self.b.distribution, -0.5)

    def test_betadistribution_distribution2(self):
        self.assertRaisesRegexp(Exception, "Distributions are computed between 0 and 1...", self.b.distribution, 1.2)

    def test_betadistribution_distribution3(self):
        self.assertEquals(self.alphalessthan1.distribution(0), 0, "error limit case alpha < 1")

    def test_betadistribution_distribution4(self):
        self.assertEquals(self.betalessthan1.distribution(1), 0, "error limit case beta < 1")

if __name__ == '__main__':
    unittest.main()

