import sys
import os
import unittest

# מוסיפים את תיקיית השורש ל-PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# מחפשים ומריצים את כל הטסטים בתיקיית tests
loader = unittest.TestLoader()
suite = loader.discover('tests')

runner = unittest.TextTestRunner()
result = runner.run(suite)

if not result.wasSuccessful():
    sys.exit(1)
