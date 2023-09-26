import unittest

def create_test_suite():
    loader = unittest.TestLoader()
    start_dir = "tests" 
    suite = loader.discover(start_dir, pattern="test_*.py")
    return suite

if __name__ == "__main__":
    test_suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
