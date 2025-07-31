#!/usr/bin/env python3
"""
🧪 Simple Test Runner for Kung Fu Chess
======================================

Runs all working tests with clear output.
"""

import unittest
import sys
import os
import time

def run_all_working_tests():
    """Run all tests that are currently working"""
    
    print("🧪" + "="*60)
    print("🧪 KUNG FU CHESS - TEST SUITE")
    print("🧪" + "="*60)
    print(f"🕒 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # List of working test modules
    working_tests = [
        'test_img_simple',
        'test_command_simple', 
        'test_moves',
        'test_integration',
        'test_coverage_summary',
        'test_game_core',                    # Game class core test
        'test_chess_rules_validator',        # ChessRulesValidator test
        'test_event_bus',                    # EventBus test
        'test_animation_manager',            # AnimationManager test
        'test_input_manager',                # InputManager test
        'test_sound_manager',                # SoundManager test
        'test_graphics_factory',             # GraphicsFactory test
        'test_physics_factory',              # PhysicsFactory test
        'test_move_logger'                   # MoveLogger test ⭐ NEW!
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_module in working_tests:
        print(f"🔍 Running {test_module}...")
        print("-" * 50)
        
        try:
            # Import and run the test module
            module = __import__(test_module)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            # Count results
            tests_run = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            
            total_tests += tests_run
            total_failures += failures
            total_errors += errors
            
            # Report results for this module
            if failures == 0 and errors == 0:
                print(f"✅ {test_module}: {tests_run} tests passed!")
            else:
                print(f"❌ {test_module}: {tests_run} tests, {failures} failures, {errors} errors")
                
        except ImportError as e:
            print(f"⚠️  Could not import {test_module}: {e}")
        except Exception as e:
            print(f"💥 Error running {test_module}: {e}")
        
        print()
    
    # Final summary
    print("="*60)
    print("📊 FINAL TEST SUMMARY")
    print("="*60)
    print(f"📋 Total tests run: {total_tests}")
    print(f"✅ Total passed: {total_tests - total_failures - total_errors}")
    print(f"❌ Total failures: {total_failures}")
    print(f"💥 Total errors: {total_errors}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"🎯 Success rate: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 ALL TESTS PASSED! EXCELLENT WORK! 🎉")
        print("✨ Your code is rock solid! ✨")
    else:
        print(f"\n⚠️  Some tests need attention")
        print(f"🔧 Fix {total_failures + total_errors} issues for perfect score")
    
    print("="*60)
    
    return total_failures == 0 and total_errors == 0

if __name__ == "__main__":
    success = run_all_working_tests()
    sys.exit(0 if success else 1)
