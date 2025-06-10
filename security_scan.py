#!/usr/bin/env python3
"""
Security scanning script for the Gamer CV API
Performs various security checks on the codebase
"""
import os
import sys
import subprocess
import json
from datetime import datetime

def banner(message):
    """Print a banner with the given message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def run_command(command, description):
    """Run a command and return its output"""
    banner(description)
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=False, 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("ERRORS:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {description}: {e}")
        return False

def main():
    """Main function to run security checks"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    banner(f"Security Scan Started at {timestamp}")
    
    # Directory to save reports
    reports_dir = "security_reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Check if all required tools are installed
    tools = ["bandit", "safety"]
    missing_tools = []
    
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True)
        except FileNotFoundError:
            missing_tools.append(tool)
    
    if missing_tools:
        banner("Missing Security Tools")
        print(f"Please install the following tools: {', '.join(missing_tools)}")
        print("You can install them using: pip install " + " ".join(missing_tools))
        sys.exit(1)
    
    # Run security checks
    results = {}
    
    # 1. Dependencies vulnerability scan
    results["dependencies"] = run_command(
        "safety check -r requirements.txt --json > " + 
        os.path.join(reports_dir, "dependencies.json"),
        "Checking Dependencies for Known Vulnerabilities"
    )
    
    # 2. Code security analysis
    results["code_security"] = run_command(
        "bandit -r . -x tests/ -f json -o " + 
        os.path.join(reports_dir, "bandit.json"),
        "Running Static Security Analysis"
    )
    
    # 3. Check for hardcoded secrets (basic check)
    results["secrets"] = run_command(
        (
            "grep -r -E '(password|secret|key|token).*=.*[\"\\']' "
            "--include='*.py' . || echo 'No potential secrets found'"
        ),
        "Checking for Hardcoded Secrets (Basic Scan)"
    )
    
    # Summary
    banner("Security Scan Summary")
    all_passed = all(results.values())
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check.replace('_', ' ').title()}: {status}")
    
    print(f"\nDetailed reports saved in the '{reports_dir}' directory.")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
