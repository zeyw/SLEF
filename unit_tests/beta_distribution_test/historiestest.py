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

from beta_distribution.History import *

class  HistoriesTestCase(unittest.TestCase):
    #def setUp(self):
    #    self.foo = Histories()
    #

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_histories_not_integer1(self):
        self.assertRaisesRegexp(Exception, "History is made by integers/long only!", History, 1.4, 1)

    def test_histories_not_integer2(self):
        self.assertRaisesRegexp(Exception, "History is made by integers/long only!", History, 1, 1.5)

    def test_histories_not_integer3(self):
        self.assertRaisesRegexp(Exception, "History is made by integers/long only!", History, 1.33, 1.5)

    def test_histories_negative1(self):
        self.assertRaisesRegexp(Exception, "History requires an history!", History, 0, -1)

    def test_histories_negative2(self):
        self.assertRaisesRegexp(Exception, "History requires an history!", History, -1, 0)

    def test_histories_negative3(self):
        self.assertRaisesRegexp(Exception, "History requires an history!", History, -1, -1)

    

if __name__ == '__main__':
    unittest.main()

