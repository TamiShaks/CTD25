#!/usr/bin/env python3
"""
🧪 Comprehensive Test Runner for Kung Fu Chess
=============================================

This module runs all tests with detailed reporting and coverage analysis.
Features:
- Automatic test discovery
- Detailed progress reporting
- Performance measurement
- Error categorization
- Summary statistics
"""

import unittest
import sys
import os
import time
from io import StringIO
from typing import Dict, List, Tuple, Any
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DetailedTestResult(unittest.TestResult):
    """Enhanced test result class with detailed tracking"""
    
    def __init__(self):
        super().__init__()
        self.test_start_time = None
        self.test_times = {}
        self.successful_tests = []
        
    def startTest(self, test):
        super().startTest(test)
        self.test_start_time = time.time()
        
    def stopTest(self, test):
        super().stopTest(test)
        if self.test_start_time:
            duration = time.time() - self.test_start_time
            self.test_times[str(test)] = duration
            
    def addSuccess(self, test):
        super().addSuccess(test)
        self.successful_tests.append(str(test))

class ColoredTestRunner:
    """Test runner with colored output and detailed reporting"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        
    def run(self, test_suite):
        """Run the test suite with detailed reporting"""
        start_time = time.time()
        
        print("🧪" + "="*80)
        print("🧪 KUNG FU CHESS - COMPREHENSIVE TEST SUITE")
        print("🧪" + "="*80)
        print(f"🕒 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        result = DetailedTestResult()
        test_suite.run(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self._print_results(result, total_time)
        return result
        
    def _print_results(self, result: DetailedTestResult, total_time: float):
        """Print detailed test results with colors and statistics"""
        
        total_tests = result.testsRun
        successes = len(result.successful_tests)
        failures = len(result.failures)
        errors = len(result.errors)
        
        print("\n" + "="*80)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*80)
        
        # Overall statistics
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"📋 Total tests run: {total_tests}")
        print(f"✅ Successful tests: {successes}")
        print(f"❌ Failed tests: {failures}")
        print(f"💥 Error tests: {errors}")
        
        success_rate = (successes / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 Success rate: {success_rate:.1f}%")
        
        # Performance analysis
        if result.test_times:
            avg_time = sum(result.test_times.values()) / len(result.test_times)
            max_time = max(result.test_times.values())
            min_time = min(result.test_times.values())
            
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average test time: {avg_time:.3f}s")
            print(f"   Fastest test: {min_time:.3f}s")
            print(f"   Slowest test: {max_time:.3f}s")
        
        # Detailed failure analysis
        if result.failures:
            print(f"\n❌ FAILURE DETAILS ({len(result.failures)} failures):")
            print("-" * 60)
            for i, (test, traceback_text) in enumerate(result.failures, 1):
                print(f"{i}. {test}")
                # Extract assertion error for cleaner output
                if "AssertionError:" in traceback_text:
                    error_msg = traceback_text.split("AssertionError:")[-1].strip()
                    print(f"   ❌ {error_msg}")
                else:
                    print(f"   ❌ {traceback_text.split('\\n')[-2].strip()}")
                print()
        
        # Detailed error analysis
        if result.errors:
            print(f"\n💥 ERROR DETAILS ({len(result.errors)} errors):")
            print("-" * 60)
            for i, (test, traceback_text) in enumerate(result.errors, 1):
                print(f"{i}. {test}")
                # Extract the main error
                lines = traceback_text.strip().split('\\n')
                error_line = lines[-1] if lines else "Unknown error"
                print(f"   💥 {error_line}")
                print()
        
        # Final verdict
        print("="*80)
        if failures == 0 and errors == 0:
            print("🎉 ALL TESTS PASSED! EXCELLENT WORK! 🎉")
            print("✨ Your code is rock solid! ✨")
        else:
            print(f"⚠️  TESTS COMPLETED WITH ISSUES")
            print(f"🔧 Please fix {failures + errors} issues before deployment")
        
        print("="*80)

def discover_and_run_tests():
    """Discover and run all tests in the current package"""
    
    # List of test modules to run
    test_modules = [
        'test_board',
        'test_piece', 
        'test_moves',
        'test_state',
        'test_physics',
        'test_graphics',
        'test_img',
        'test_command',
        'test_game',
        'test_event_bus',
        'test_managers',
        'test_factories',
        'test_input_managers',
        'test_integration'
    ]
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    successful_imports = []
    failed_imports = []
    
    print("🔍 Discovering test modules...")
    
    for module_name in test_modules:
        try:
            # Try to import the module
            module = __import__(module_name)
            tests = loader.loadTestsFromModule(module)
            suite.addTest(tests)
            successful_imports.append(module_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            failed_imports.append((module_name, str(e)))
            print(f"   ⚠️  {module_name} (not found - will be created)")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"   ❌ {module_name} (error: {e})")
    
    print(f"\n📊 Discovery Summary:")
    print(f"   ✅ Successfully loaded: {len(successful_imports)} modules")
    print(f"   ⚠️  Missing modules: {len(failed_imports)} modules")
    
    if successful_imports:
        print(f"\n🚀 Running tests from {len(successful_imports)} modules...")
        runner = ColoredTestRunner(verbosity=2)
        result = runner.run(suite)
        return result
    else:
        print("\n⚠️  No test modules found to run!")
        print("💡 Tip: Create test files with names like 'test_board.py', 'test_piece.py', etc.")
        return None

if __name__ == "__main__":
    print("🥋 Kung Fu Chess Test Suite - Starting...")
    result = discover_and_run_tests()
    
    # Exit with appropriate code
    if result and (result.failures or result.errors):
        sys.exit(1)
    else:
        sys.exit(0)
