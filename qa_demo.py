#!/usr/bin/env python3
"""
E-Shop Checkout QA Demo Script
Demonstrates the complete autonomous QA testing framework

This script shows how to:
1. Use the RAG system to retrieve relevant documentation
2. Generate test cases based on user queries
3. Create Selenium automation scripts
4. Run automated tests

Run with: python3 qa_demo.py
"""

import json
import os
from pathlib import Path
from test_case_generator import RAGSystem, TestCaseGenerator
from selenium_automation import generate_selenium_script_for_test, CheckoutTestAutomation, SeleniumTestCase


def demo_rag_retrieval():
    """Demonstrate document retrieval and RAG functionality."""
    print("🔍 DEMO: Document Retrieval and RAG System")
    print("=" * 60)
    
    # Initialize RAG system
    rag_system = RAGSystem()
    rag_system.load_documents()
    
    print(f"📚 Loaded {len(rag_system.document_chunks)} document chunks from:")
    for filename in rag_system.supported_files:
        file_path = Path(rag_system.workspace_path) / filename
        if file_path.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (not found)")
    
    print()
    
    # Demo retrieval for different queries
    test_queries = [
        "discount code SAVE15",
        "Pay Now button color",
        "email validation error message",
        "Express shipping cost"
    ]
    
    for query in test_queries:
        print(f"🔎 Query: '{query}'")
        relevant_chunks = rag_system.retrieve_relevant_chunks(query, top_k=3)
        print(f"   Found {len(relevant_chunks)} relevant chunks:")
        
        for i, chunk in enumerate(relevant_chunks, 1):
            print(f"   {i}. {chunk.source_document}#{chunk.section} - {chunk.content[:100]}...")
        print()


def demo_test_case_generation():
    """Demonstrate automated test case generation."""
    print("🧪 DEMO: Test Case Generation")
    print("=" * 60)
    
    # Initialize components
    rag_system = RAGSystem()
    rag_system.load_documents()
    generator = TestCaseGenerator(rag_system)
    
    # Example queries for different features
    sample_queries = [
        "Generate positive and negative test cases for discount code feature",
        "Generate validation test cases for form fields",
        "Generate cart management test cases",
        "Generate payment processing test cases"
    ]
    
    for query in sample_queries:
        print(f"📝 Generating tests for: '{query}'")
        test_cases = generator.generate_test_cases(query)
        
        print(f"   ✅ Generated {len(test_cases)} test cases")
        if test_cases:
            # Show first test case as example
            first_test = test_cases[0]
            print(f"   Example: {first_test.get('Test_ID', 'N/A')} - {first_test.get('Test_Scenario', 'N/A')}")
            print(f"   Grounded in: {', '.join(first_test.get('Grounded_In', []))[:100]}...")
        print()


def demo_selenium_script_generation():
    """Demonstrate Selenium script generation for specific test cases."""
    print("🤖 DEMO: Selenium Script Generation")
    print("=" * 60)
    
    # Load comprehensive test cases
    test_cases_file = Path("comprehensive_test_cases.json")
    if not test_cases_file.exists():
        print("❌ comprehensive_test_cases.json not found")
        return
    
    with open(test_cases_file, 'r') as f:
        test_cases = json.load(f)
    
    # Generate scripts for different types of tests
    demo_tests = [
        ("Discount Code Test", lambda tc: tc.get("Feature") == "Discount Code"),
        ("Form Validation Test", lambda tc: tc.get("Feature") == "Validation"),
        ("Payment Test", lambda tc: tc.get("Feature") == "Payment")
    ]
    
    for demo_name, filter_func in demo_tests:
        matching_tests = [tc for tc in test_cases if filter_func(tc)]
        if matching_tests:
            test_case = matching_tests[0]
            print(f"🔧 Generating {demo_name} script for: {test_case['Test_ID']}")
            
            script = generate_selenium_script_for_test(test_case)
            script_lines = script.split('\n')
            
            # Show key parts of the generated script
            print(f"   Script contains {len(script_lines)} lines")
            print(f"   Test function: test_{test_case['Test_ID'].lower().replace('-', '_')}")
            print(f"   Expected result: {test_case['Expected_Result'][:100]}...")
            print()


def demo_live_test_execution():
    """Demonstrate live test execution (optional - requires Chrome)."""
    print("🚀 DEMO: Live Test Execution")
    print("=" * 60)
    
    try:
        # Check if checkout.html exists
        checkout_file = Path("checkout.html")
        if not checkout_file.exists():
            print("❌ checkout.html not found - skipping live test demo")
            return
        
        print("🌐 Setting up test automation...")
        
        # Create simple test case for demo
        demo_test_case = {
            "Test_ID": "DEMO-001",
            "Feature": "Cart",
            "Test_Scenario": "Add laptop to cart and verify total",
            "Steps": [
                "Select Laptop from dropdown",
                "Set quantity to 1",
                "Click Add to Cart",
                "Verify total shows $999.99"
            ],
            "Expected_Result": "Laptop added to cart with correct price calculation",
            "Grounded_In": ["product_specs.md#cart_item_management"]
        }
        
        # Note: Actual execution would require Chrome/ChromeDriver
        print("📋 Demo test case created:")
        print(f"   Test ID: {demo_test_case['Test_ID']}")
        print(f"   Feature: {demo_test_case['Feature']}")
        print(f"   Scenario: {demo_test_case['Test_Scenario']}")
        print()
        print("🔧 To run live tests, install:")
        print("   pip install selenium webdriver-manager")
        print("   Then use: CheckoutTestAutomation and SeleniumTestCase classes")
        
    except Exception as e:
        print(f"⚠️  Live test demo skipped: {e}")


def demo_grounding_validation():
    """Demonstrate strict grounding requirements."""
    print("📊 DEMO: Grounding and Citation Validation")
    print("=" * 60)
    
    # Load test cases and validate grounding
    test_cases_file = Path("comprehensive_test_cases.json")
    if test_cases_file.exists():
        with open(test_cases_file, 'r') as f:
            test_cases = json.load(f)
        
        print(f"📋 Analyzing {len(test_cases)} test cases for grounding...")
        
        # Check grounding compliance
        grounding_stats = {
            "product_specs.md": 0,
            "ui_ux_guide.txt": 0,
            "checkout.html": 0,
            "api_endpoints.json": 0
        }
        
        missing_grounding = []
        
        for test_case in test_cases:
            grounding = test_case.get("Grounded_In", [])
            
            if not grounding:
                missing_grounding.append(test_case.get("Test_ID", "Unknown"))
            else:
                for ground_ref in grounding:
                    for doc_type in grounding_stats:
                        if doc_type in ground_ref:
                            grounding_stats[doc_type] += 1
        
        print("📈 Grounding distribution:")
        for doc_type, count in grounding_stats.items():
            print(f"   {doc_type}: {count} references")
        
        if missing_grounding:
            print(f"⚠️  Tests missing grounding: {', '.join(missing_grounding)}")
        else:
            print("✅ All tests properly grounded")
        
        # Check for "Not specified" handling
        not_specified_count = 0
        for test_case in test_cases:
            test_content = json.dumps(test_case)
            if "Not specified" in test_content:
                not_specified_count += 1
        
        print(f"📝 Tests with 'Not specified' elements: {not_specified_count}")
        print()
    else:
        print("❌ Test cases file not found")


def main():
    """Run complete QA framework demonstration."""
    print("🎯 E-Shop Checkout - Autonomous QA Framework Demo")
    print("=" * 70)
    print("Building comprehensive test cases from provided context.")
    print("Grounding strictly in documentation. No feature invention.")
    print("=" * 70)
    print()
    
    # Run all demonstrations
    demo_rag_retrieval()
    demo_test_case_generation()
    demo_selenium_script_generation()
    demo_grounding_validation()
    demo_live_test_execution()
    
    print("✨ DEMO COMPLETE")
    print("=" * 60)
    print("Framework ready for:")
    print("• RAG-based test case generation")
    print("• Comprehensive test coverage (30+ test cases)")
    print("• Selenium automation with stable selectors")
    print("• Strict grounding in provided documentation")
    print("• JSON schema compliance")
    print()
    print("Key files:")
    print("• checkout.html - Single-page E-Shop application")
    print("• comprehensive_test_cases.json - Complete test suite")
    print("• test_case_generator.py - RAG system")
    print("• selenium_automation.py - Test automation")
    print()
    print("Ready to respond to user queries like:")
    print('• "Generate all positive and negative test cases for discount code feature"')
    print('• "Generate Selenium script for TC-001"')
    print('• "Test the Pay Now button color requirement"')


if __name__ == "__main__":
    main()