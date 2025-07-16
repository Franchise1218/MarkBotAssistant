#!/usr/bin/env python3
"""
Test script to demonstrate Mark.py functionality
"""

import sys
import os
sys.path.append('.')

from Mark import *

def test_mark_functionality():
    print("🤖 Testing Mark.py functionality...")
    print("="*50)
    
    # Initialize database if needed
    if not os.path.exists(db_file):
        print("⚙️ MARK needs his brain installed...")
        refresh_sql_from_excel()
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    print("Command: search:matrix")
    results = search_sql_data("matrix")
    if results:
        for score, row in results[:3]:  # Show top 3 results
            print(f"Match ({score}%): {dict(row)}")
    else:
        print("No results found for 'matrix'")
    
    print("\n" + "="*50)
    
    # Test disc lookup
    print("\n💿 Testing disc lookup...")
    print("Command: disc:DVD001")
    df = get_disc("DVD001")
    if not df.empty:
        print("Disc found:")
        print(df.to_string(index=False))
    else:
        print("No disc found for DVD001")
    
    print("\n" + "="*50)
    
    # Test count functionality
    print("\n📦 Testing count functionality...")
    print("Command: count:star")
    count = count_discs("star")
    print(f"'star' appears {count} times")
    
    print("\n" + "="*50)
    
    # Test first disc
    print("\n🎯 Testing first disc...")
    print("Command: first disc:godfather")
    result = first_disc("godfather")
    if result is not None:
        print(f"First match: {dict(result)}")
    else:
        print("No match found for 'godfather'")
    
    print("\n" + "="*50)
    
    # Test autograph search
    print("\n✍️ Testing autograph search...")
    print("Command: autograph:pacino")
    results = search_autograph_data("pacino")
    if results:
        for score, row in results[:3]:
            print(f"Autograph match ({score}%): {dict(row)}")
    else:
        print("No autographs found for 'pacino'")

if __name__ == "__main__":
    test_mark_functionality()