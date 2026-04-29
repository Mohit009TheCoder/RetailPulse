#!/usr/bin/env python3
"""
Verify RFM Customer Segmentation System Setup
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def main():
    print("=" * 60)
    print("RFM Customer Segmentation System - Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python files
    print("📄 Checking Python files...")
    all_good &= check_file("app.py", "Flask application")
    all_good &= check_file("rfm_analysis.py", "RFM analysis module")
    all_good &= check_file("requirements.txt", "Requirements file")
    print()
    
    # Check data file
    print("📊 Checking data files...")
    all_good &= check_file("cleandataset.csv", "Customer data CSV")
    print()
    
    # Check directories
    print("📁 Checking directories...")
    all_good &= check_directory("templates", "Templates directory")
    all_good &= check_directory("static", "Static directory")
    all_good &= check_directory("static/css", "CSS directory")
    all_good &= check_directory("static/js", "JavaScript directory")
    print()
    
    # Check template files
    print("📝 Checking template files...")
    all_good &= check_file("templates/base.html", "Base template")
    all_good &= check_file("templates/index.html", "Dashboard template")
    all_good &= check_file("templates/segments.html", "Segments template")
    all_good &= check_file("templates/customers.html", "Customers template")
    all_good &= check_file("templates/about.html", "About template")
    print()
    
    # Check static files
    print("🎨 Checking static files...")
    all_good &= check_file("static/css/style.css", "CSS stylesheet")
    all_good &= check_file("static/js/main.js", "Main JavaScript")
    all_good &= check_file("static/js/dashboard.js", "Dashboard JavaScript")
    all_good &= check_file("static/js/segments.js", "Segments JavaScript")
    all_good &= check_file("static/js/customers.js", "Customers JavaScript")
    print()
    
    # Check Python packages
    print("📦 Checking Python packages...")
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError:
        print("❌ Flask: Not installed")
        all_good = False
    
    try:
        import pandas
        print(f"✅ Pandas: {pandas.__version__}")
    except ImportError:
        print("❌ Pandas: Not installed")
        all_good = False
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
        all_good = False
    print()
    
    # Final result
    print("=" * 60)
    if all_good:
        print("✅ All checks passed! System is ready to run.")
        print()
        print("To start the application, run:")
        print("  python app.py")
        print()
        print("Or use the convenience script:")
        print("  ./run.sh")
        print()
        print("Then open your browser to: http://localhost:5000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()
        print("To install missing packages, run:")
        print("  pip install -r requirements.txt")
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
