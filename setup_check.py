"""
Setup verification script
Checks that all dependencies are installed and configured
"""

import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    missing = []

    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        missing.append("requests")
        print("  ✗ requests")

    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        missing.append("openai")
        print("  ✗ openai")

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        missing.append("python-dotenv")
        print("  ✗ python-dotenv")

    return missing

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\nChecking environment configuration...")

    if not os.path.exists(".env"):
        print("  ✗ .env file not found")
        print("\nTo create .env file:")
        print("  1. Copy .env.example to .env:")
        print("     cp .env.example .env")
        print("  2. Edit .env and add your OpenAI API key:")
        print("     OPENAI_API_KEY=your_actual_key_here")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return False

    print("  ✓ .env file exists")

    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("  ✗ OPENAI_API_KEY not set or using placeholder value")
        print("\nEdit .env and add your actual OpenAI API key")
        return False

    print("  ✓ OPENAI_API_KEY is set")
    return True

def check_data():
    """Check if POI data exists and is enriched"""
    print("\nChecking data files...")

    if not os.path.exists("data/richmond_pois.json"):
        print("  ✗ richmond_pois.json not found")
        print("  Run: python src/create_sample_data.py")
        return False

    print("  ✓ richmond_pois.json exists")

    import json
    with open("data/richmond_pois.json", 'r') as f:
        data = json.load(f)

    enriched_count = data["metadata"].get("enriched_pois", 0)
    if enriched_count < 10:
        print(f"  ⚠ Only {enriched_count} POIs enriched (need 10)")
        print("  Run: python src/enrich_pois.py")
        return False

    print(f"  ✓ {enriched_count} POIs enriched")
    return True

def main():
    print("Richmond Walking Tour - Setup Check")
    print("="*60)

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n✗ Missing packages: {', '.join(missing)}")
        print("\nInstall missing packages:")
        print(f"  pip install {' '.join(missing)}")
        return False

    # Check environment
    env_ok = check_env_file()

    # Check data
    data_ok = check_data()

    print("\n" + "="*60)
    if env_ok and data_ok:
        print("✓ Setup complete! Ready to generate tours.")
        print("\nRun: python src/generate_tour.py")
        return True
    else:
        print("✗ Setup incomplete. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
