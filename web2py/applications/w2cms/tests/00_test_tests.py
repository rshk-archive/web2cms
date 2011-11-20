"""unittest tests to see if tests work.

We need to use TestSuite this way since unittest.main() gets confused
by web2py execfile(), that is needed in order to access web2py stuff.
"""

import unittest

class MyExampleTest(unittest.TestCase):
    def test_exampletest(self):
        """Test if tests work"""
        self.assertEqual(True, True)
    
    def test_importmodule(self):
        """Try to import a module from application modules directory"""
        try:
            import cms_tools
        except ImportError:
            self.assert_(False, "Unable to load module cms_tools")
        else:
            self.assert_(True, "Successfully loaded cms_tools")

class MyExampleTest2(unittest.TestCase):
    def test_exampletest2(self):
        """Second test to check multi-test suites"""
        self.assertEqual(True, True)


if __name__ == '__main__':
    suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(MyExampleTest),
        unittest.TestLoader().loadTestsFromTestCase(MyExampleTest2),
    ])
    unittest.TextTestRunner(verbosity=2).run(suite)
