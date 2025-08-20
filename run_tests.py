#!/usr/bin/env python3
"""
Test runner script for Subsplash Calendar Bridge.
This script provides an easy way to run different types of tests.
"""

import sys
import os

def show_menu():
    """Show the test menu"""
    print("🧪 Subsplash Calendar Bridge - Test Runner")
    print("=" * 50)
    print("Choose a test to run:")
    print("1. 🔧 Basic Functionality Test - Test configuration and authentication")
    print("2. 🌐 Scraping Test - Test Subsplash event scraping")
    print("3. 🔄 Dry Run Sync - Simulate full sync without making changes")
    print("4. 📅 Date Parsing Test - Test date parsing accuracy")
    print("5. 🎯 Test Specific Calendar - Test a single calendar")
    print("6. 🚀 Run All Tests - Comprehensive testing")
    print("0. ❌ Exit")
    print("=" * 50)

def run_basic_test():
    """Run the basic functionality test"""
    print("Running basic functionality test...")
    os.system("python test_sync_functionality.py")

def run_scraping_test():
    """Run the scraping test"""
    print("Running scraping test...")
    os.system("python test_sync_browser_navigation.py")

def run_dry_run_sync():
    """Run the dry-run sync test"""
    print("Running dry-run sync test...")
    os.system("python test_dry_run_sync.py")

def run_date_parsing_test():
    """Run the date parsing test"""
    print("Running date parsing test...")
    os.system("python test_date_parsing.py")

def test_specific_calendar():
    """Test a specific calendar"""
    enabled_calendars = []
    try:
        from sync_script import get_enabled_calendars
        calendars = get_enabled_calendars()
        enabled_calendars = list(calendars.keys())
    except:
        print("❌ Could not load calendar configuration")
        return
    
    if not enabled_calendars:
        print("❌ No enabled calendars found")
        return
    
    print("Available calendars:")
    for i, cal_key in enumerate(enabled_calendars):
        print(f"  {i+1}. {cal_key.upper()}")
    
    try:
        choice = input("\nEnter calendar number (or 'all'): ").strip().lower()
        if choice == 'all':
            os.system("python test_dry_run_sync.py")
        elif choice.isdigit():
            cal_index = int(choice) - 1
            if 0 <= cal_index < len(enabled_calendars):
                cal_key = enabled_calendars[cal_index]
                print(f"Testing calendar: {cal_key}")
                os.system(f"python test_dry_run_sync.py {cal_key}")
            else:
                print("❌ Invalid calendar number")
        else:
            print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\nCancelled")

def run_all_tests():
    """Run all tests in sequence"""
    print("Running all tests...")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", "python test_sync_functionality.py"),
        ("Date Parsing", "python test_date_parsing.py"),
        ("Dry Run Sync", "python test_dry_run_sync.py")
    ]
    
    for test_name, command in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        result = os.system(command)
        if result == 0:
            print(f"✅ {test_name} completed successfully")
        else:
            print(f"❌ {test_name} failed")
        
        input("Press Enter to continue to next test...")

def main():
    """Main test runner function"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_basic_test()
            elif choice == "2":
                run_scraping_test()
            elif choice == "3":
                run_dry_run_sync()
            elif choice == "4":
                run_date_parsing_test()
            elif choice == "5":
                test_specific_calendar()
            elif choice == "6":
                run_all_tests()
            else:
                print("❌ Invalid choice. Please enter a number between 0-6.")
            
            if choice != "0":
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Error: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
