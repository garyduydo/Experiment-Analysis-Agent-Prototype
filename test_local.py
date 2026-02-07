#!/usr/bin/env python3
"""
Local Test Script for Experiment Analyzer
Run this to test the API locally before deploying
"""

import os
import sys
import json
import requests
import time
from subprocess import Popen, PIPE
import signal

def test_local_server():
    """Test the Flask server locally"""
    
    print(" Testing Experiment Analyzer Locally")
    print("="*60)
    
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print(" ERROR: GROQ_API_KEY not set!")
        print("\nSet it with:")
        print("  export GROQ_API_KEY='your_key_here'")
        print("\nGet a free key at: https://console.groq.com")
        sys.exit(1)
    
    print(f" Groq API key found: {groq_key[:10]}...")
    
    print("\n Starting Flask server...")
    server = Popen(['python', 'api.py'], stdout=PIPE, stderr=PIPE)
    
    print(" Waiting for server to start...")
    time.sleep(3)
    
    try:
        print("\n Testing health endpoint...")
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print(" Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f" Health check failed: {response.status_code}")
        
        print("\n Testing analysis endpoint...")
        test_data = {
            "experiment_name": "Test Experiment",
            "hypothesis": "This is a test",
            "start_date": "2024-01-01",
            "end_date": "2024-01-14",
            "variants": {
                "control": {
                    "name": "Control",
                    "users": 1000,
                    "conversions": 100,
                    "conversion_rate": 0.10,
                    "revenue_per_user": 10.00
                },
                "variant_a": {
                    "name": "Variant A",
                    "users": 1000,
                    "conversions": 150,
                    "conversion_rate": 0.15,
                    "revenue_per_user": 15.00
                }
            }
        }
        
        print(" Sending test data to API...")
        response = requests.post(
            'http://localhost:5000/api/analyze',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print(" Analysis completed successfully!")
            result = response.json()
            print(f"\n RESULTS:")
            print(f"   Executive Summary: {result.get('executive_summary', 'N/A')[:100]}...")
            print(f"   Winner: {result.get('statistical_results', {}).get('winner', 'N/A')}")
            print(f"   Lift: {result.get('statistical_results', {}).get('lift', 'N/A')}")
            print("\n ALL TESTS PASSED!")
            print("\n Your API is working! Ready to deploy!")
        else:
            print(f" Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f" Test failed: {e}")
        print("\nCommon issues:")
        print("  - Is GROQ_API_KEY set correctly?")
        print("  - Did you install dependencies? (pip install -r requirements.txt)")
        print("  - Is port 5000 already in use?")
    
    finally:
        print("\n Stopping server...")
        server.send_signal(signal.SIGTERM)
        server.wait()
        print(" Server stopped")
    
    print("\n" + "="*60)
    print(" Next steps:")
    print("  1. Push code to GitHub")
    print("  2. Deploy to Render or Railway")
    print("  3. Set GROQ_API_KEY in your deployment")
    print("  4. Visit your deployment URL!")
    print("\nSee QUICKSTART.md for detailed instructions.")


if __name__ == "__main__":
    test_local_server()