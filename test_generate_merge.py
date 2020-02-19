#! /usr/bin/env python
import unittest
import generate_merge as gm

class MyTestCase(unittest.TestCase):
    def test_bar(self):
        val = gm.dest_src_split("a: b ")
        self.assertEqual("a", val[0])
        self.assertEqual("b", val[1])

if __name__ == '__main__':
    unittest.main()
