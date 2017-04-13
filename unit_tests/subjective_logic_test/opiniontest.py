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
from subjective_logic.NotAnOpinionException import *
from subjective_logic.Opinion import *


class  OpinionTestCase(unittest.TestCase):
    def setUp(self):
        self.third = Opinion("1/3","1/3","1/3","1/3")
        self.disbelief = Opinion("0", "1", "0", "1/2")
    

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_opinion_violating_belief(self):
        self.assertRaises(NotAnOpinionException, Opinion, "2", "0", "0", "0")

    def test_opinion_violating_disbelief(self):
        self.assertRaises(NotAnOpinionException, Opinion, "0", "2", "0", "0")

    def test_opinion_violating_uncertainty(self):
        self.assertRaises(NotAnOpinionException, Opinion, "0", "0", "2", "0")

    def test_opinion_violating_base(self):
        self.assertRaises(NotAnOpinionException, Opinion, "0", "0", "0", "2")

    def test_opinion_violating_sum(self):
        self.assertRaises(NotAnOpinionException, Opinion, "0.7", "0.7", "0.7", "0")

    def test_opinion_non_violating_sum(self):
        try:
            Opinion("1/3","1/3","1/3","0")
        except NotAnOpinionException as e:
            self.fail("lack of precision: " + e.__str__())
        pass
    
    def test_opinion_third_alpha(self):
        self.assertTrue(mpmath.almosteq(self.third.get_angle_alpha(), (mpmath.pi/6), epsilon), "alpha angle of " + repr(self.third) + " not correctly computed. It should be: " + repr((mpmath.pi/6)) + " but it is: " + repr(self.third.get_angle_alpha()))
        
    def test_opinion_third_beta(self):
        self.assertTrue(mpmath.almosteq(self.third.get_angle_beta(), (mpmath.pi/6), epsilon), "beta angle of " + repr(self.third) + " not correctly computed. It should be: " + repr((mpmath.pi/6)) + " but it is: " + repr(self.third.get_angle_beta()))
        
    def test_opinion_third_gamma(self):
        self.assertTrue(mpmath.almosteq(self.third.get_angle_gamma(), (mpmath.pi/6), epsilon), "gamma angle of " + repr(self.third) + " not correctly computed. It should be: " + repr((mpmath.pi/6)) + " but it is: " + repr(self.third.get_angle_gamma()))

    def test_opinion_third_delta(self):
        self.assertTrue(mpmath.almosteq(self.third.get_angle_delta(), (mpmath.pi/6), epsilon), "delta angle of " + repr(self.third) + " not correctly computed. It should be: " + repr((mpmath.pi/6)) + " but it is: " + repr(self.third.get_angle_delta()))
        
    def test_opinion_third_epsilon(self):
        self.assertTrue(mpmath.almosteq(self.third.get_angle_epsilon(), (2 * mpmath.pi/3), epsilon), "epsilon angle of " + repr(self.third) + " not correctly computed. It should be: " + repr((2 * mpmath.pi/3)) + " but it is: " + repr(self.third.get_angle_epsilon()))
        
    def test_opinion_third_length_to_uncertainty(self):
        self.assertTrue(mpmath.almosteq(self.third.get_length_to_uncertainty(), mpmath.mpf("2/3"), epsilon), "length to uncertainty of " + repr(self.third) + " not correctly computed. It should be: 2/3, but it is: " + repr(self.third.get_length_to_uncertainty()))

    def test_opinion_disbelief_alpha(self):
        self.assertTrue(mpmath.almosteq(self.disbelief.get_angle_alpha(), (mpmath.mpf("0")), epsilon), "alpha angle of " + repr(self.disbelief) + " not correctly computed. It should be: " + repr((mpmath.mpf("0"))) + " but it is: " + repr(self.disbelief.get_angle_alpha()))
        
    def test_opinion_almost_zero(self):
        try:
            Opinion("-2.22044604925031e-16", "-2.30077316370261e-15", "1.0", "0.5")
        except NotAnOpinionException as e:
            self.fail(e.__str__())
        pass
    
    def test_expected_value(self):
        self.assertTrue(mpmath.almosteq(self.third.expected_value(), mpmath.mpf("1/3")+mpmath.mpf("1/9")), "Expected value of " + repr(self.third) + " not correctly computed: it is: " + repr(self.third.expected_value()))

if __name__ == '__main__':
    unittest.main()

