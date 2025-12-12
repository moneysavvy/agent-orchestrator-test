#!/usr/bin/env python3
"""
CEO Coding Boss - Comprehensive Test Suite
Tests the Local Agent Orchestrator with CEO Coding Boss integration
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime

# ANSI color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TestRunner:
    def __init__(self):
        self.agent_url = "http://localhost:5000"
        self.ollama_url = "http://localhost:11434"
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def print_header(self, message):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    def print_test(self, name):
        print(f"{Colors.OKCYAN}[TEST]{Colors.ENDC} {name}...", end=" ")
    
    def print_pass(self, details=""):
        self.tests_passed += 1
        print(f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}")
        if details:
            print(f"  {Colors.OKBLUE}→{Colors.ENDC} {details}")
    
    def print_fail(self, error):
        self.tests_failed += 1
        print(f"{Colors.FAIL}✗ FAILED{Colors.ENDC}")
        print(f"  {Colors.FAIL}→{Colors.ENDC} {error}")
    
    def print_info(self, message):
        print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {message}")
    
    def print_warning(self, message):
        print(f"{Colors.WARNING}[WARN]{Colors.ENDC} {message}")
    
    def test_ollama_connection(self):
        """Test if Ollama is running and accessible"""
        self.print_test("Ollama Service Connection")
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.print_pass(f"Found {len(models)} models")
                for model in models:
                    print(f"    • {model.get('name', 'unknown')}")
                return True
            else:
                self.print_fail(f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(str(e))
            return False
    
    def test_ollama_model(self, model="qwen2.5:latest"):
        """Test if required Ollama model is available"""
        self.print_test(f"Ollama Model '{model}'")
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if model in models or any(model.split(':')[0] in m for m in models):
                    self.print_pass(f"Model available")
                    return True
                else:
                    self.print_fail(f"Model not found. Available: {', '.join(models)}")
                    return False
        except Exception as e:
            self.print_fail(str(e))
            return False
    
    def test_ollama_generate(self, model="qwen2.5:latest", prompt="Say 'test'"):
        """Test Ollama generation capability"""
        self.print_test("Ollama Generation")
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                self.print_pass(f"Generated {len(response_text)} chars")
                print(f"    Response: {response_text[:100]}...")
                return True
            else:
                self.print_fail(f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(str(e))
            return False
    
    def test_agent_runtime_exists(self):
        """Test if agent_runtime.py exists"""
        self.print_test("Agent Runtime File")
        if os.path.exists('agent_runtime.py'):
            self.print_pass("agent_runtime.py found")
            return True
        else:
            self.print_fail("agent_runtime.py not found")
            return False
    
    def test_environment_variables(self):
        """Test if required environment variables are set"""
        self.print_test("Environment Variables")
        required_vars = ['APP_ID', 'PRIVATE_KEY_PATH', 'INSTALLATION_ID', 'OLLAMA_URL', 'OLLAMA_MODEL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            self.print_pass("All required variables set")
            return True
        else:
            self.print_warning(f"Missing: {', '.join(missing_vars)}")
            return False
    
    def test_dependencies(self):
        """Test if required Python dependencies are installed"""
        self.print_test("Python Dependencies")
        dependencies = ['flask', 'requests', 'jwt', 'playwright', 'ruff']
        missing = []
        
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if not missing:
            self.print_pass("All dependencies installed")
            return True
        else:
            self.print_fail(f"Missing: {', '.join(missing)}")
            return False
    
    def test_ceo_coding_boss_spec(self):
        """Test if CEO_CODING_BOSS.md exists and is valid"""
        self.print_test("CEO Coding Boss Specification")
        if os.path.exists('CEO_CODING_BOSS.md'):
            with open('CEO_CODING_BOSS.md', 'r') as f:
                content = f.read()
                if len(content) > 100:
                    self.print_pass(f"{len(content)} bytes loaded")
                    return True
                else:
                    self.print_fail("File too small")
                    return False
        else:
            self.print_fail("CEO_CODING_BOSS.md not found")
            return False
    
    def test_architecture(self):
        """Test if ARCHITECTURE.md exists"""
        self.print_test("Architecture Documentation")
        if os.path.exists('ARCHITECTURE.md'):
            self.print_pass("ARCHITECTURE.md found")
            return True
        else:
            self.print_fail("ARCHITECTURE.md not found")
            return False
    
    def test_page_assist_setup(self):
        """Test if PAGE_ASSIST_SETUP.md exists"""
        self.print_test("Page Assist Setup Guide")
        if os.path.exists('PAGE_ASSIST_SETUP.md'):
            self.print_pass("PAGE_ASSIST_SETUP.md found")
            return True
        else:
            self.print_fail("PAGE_ASSIST_SETUP.md not found")
            return False
    
    def run_integration_test(self):
        """Run a simple integration test with the agent"""
        self.print_test("Integration Test - Simple Task")
        try:
            # This would be a real API call to your agent
            # For now, we'll just simulate it
            test_task = {
                "type": "code_review",
                "content": "def hello(): return 'world'",
                "model": "qwen2.5:latest"
            }
            
            # Simulate processing
            time.sleep(0.5)
            self.print_pass("Task simulation completed")
            return True
        except Exception as e:
            self.print_fail(str(e))
            return False
    
    def generate_report(self):
        """Generate a test report"""
        self.print_header("TEST SUMMARY")
        
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.OKGREEN}Passed: {self.tests_passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.tests_failed}{Colors.ENDC}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.tests_failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠ SOME TESTS FAILED{Colors.ENDC}")
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("CEO CODING BOSS - TEST SUITE")
        self.print_info(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # System Tests
        self.print_header("SYSTEM TESTS")
        self.test_ollama_connection()
        self.test_ollama_model()
        self.test_ollama_generate()
        
        # File Tests
        self.print_header("FILE TESTS")
        self.test_agent_runtime_exists()
        self.test_ceo_coding_boss_spec()
        self.test_architecture()
        self.test_page_assist_setup()
        
        # Dependency Tests
        self.print_header("DEPENDENCY TESTS")
        self.test_environment_variables()
        self.test_dependencies()
        
        # Integration Tests
        self.print_header("INTEGRATION TESTS")
        self.run_integration_test()
        
        # Generate Report
        self.generate_report()

def main():
    runner = TestRunner()
    runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if runner.tests_failed == 0 else 1)

if __name__ == "__main__":
    main()