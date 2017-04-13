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
import mpmath

import subjective_logic.operators as operators
from subjective_logic.Opinion import Opinion

class  OperatorsTestCase(unittest.TestCase):
    def setUp(self):
        self.third = Opinion("1/3", "1/3", "1/3", "1/2")
        self.nobelief = Opinion("0","1/2","1/2","1/2")
        
        self.belief = Opinion("1", "0", "0", "1/2")
        self.disbelief = Opinion("0", "1", "0", "1/2")
        self.uncertainty = Opinion("0", "0", "1", "1/2")
        
        
        while True:
            r1 = mpmath.rand()
            r2 = mpmath.rand()
            if r1 + r2 < 1:
                self.random = Opinion(r1, r2, mpmath.mpf("1") - (r1 + r2), "1/2")
                break
            
            
    def test_operator_merge_discount1(self):
        self.assertEqual(operators.graphical_discount_merge([[self.belief, self.belief],[self.belief, self.uncertainty],[self.belief, self.disbelief]]),
                         self.third,
                         self.third.__repr__() + " is not what we got: " + operators.graphical_discount_merge([[self.belief, self.belief],[self.belief, self.uncertainty],[self.belief, self.disbelief]]).__repr__())

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_operators_discount_raise(self):
        self.assertRaisesRegexp(Exception, "Two valid Opinions are required!", operators.discount, 3, 2)

    def test_operators_discount1(self):
        a = Opinion("0", "1", "0", "1/2")
        b = Opinion("1", "0", "0", "1/2")
        c = Opinion("0", "0", "1", "1/2")
        self.assertEqual(operators.discount(a, b), c, "<0,1,0,0.5> \\ctimes <1,0,0,0.5> = "+repr(operators.discount(a, b))+" != <0,0,1,0.5> ")
        
    def test_operators_gcombination_raise(self):
        self.assertRaisesRegexp(Exception, "Two valid Opinions are required!", operators.discount, 3, 2)
        
    def test_operators_gcombination_req1(self):
        t = self.third
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_req2(self):
        t = self.third
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_req3(self):
        t = self.third
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))

        
    def test_operators_gcombination_nobelief_req1(self):
        t = self.nobelief
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_nobelief_req2(self):
        t = self.nobelief
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_nobelief_req3(self):
        t = self.nobelief
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_rand_req1(self):
        t = self.random
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_rand_req2(self):
        t = self.random
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_rand_req3(self):
        t = self.random
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_belief_req1(self):
        t = self.belief
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_belief_req2(self):
        t = self.belief
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_belief_req3(self):
        t = self.belief
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))

    def test_operators_gcombination_disbelief_req1(self):
        t = self.disbelief
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_disbelief_req2(self):
        t = self.disbelief
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_disbelief_req3(self):
        t = self.disbelief
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_uncertainty_req1(self):
        t = self.uncertainty
        c = self.belief
        r = t
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
    
    def test_operators_gcombination_uncertainty_req2(self):
        t = self.uncertainty
        c = self.disbelief
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        
    def test_operators_gcombination_uncertainty_req3(self):
        t = self.uncertainty
        c = self.uncertainty
        r = c
        self.assertEqual(operators.graphical_combination(t, c), r, repr(t) + " \\ cdot " + repr(c) +" = "+  repr(operators.graphical_combination(t, c)) +" != "+ repr(r))
        

if __name__ == '__main__':
    unittest.main()

