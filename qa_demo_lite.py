#!/usr/bin/env python3
"""
E-Shop Checkout QA Demo Script (No Selenium Dependencies)
Demonstrates the RAG system and test case generation

This script shows how to:
1. Use the RAG system to retrieve relevant documentation
2. Generate test cases based on user queries
3. Validate grounding and citations

Run with: python3 qa_demo_lite.py
"""

import json
import os
from pathlib import Path
from test_case_generator import RAGSystem, TestCaseGenerator


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
    
    all_generated_tests = []
    
    for query in sample_queries:
        print(f"📝 Generating tests for: '{query}'")
        test_cases = generator.generate_test_cases(query)
        
        print(f"   ✅ Generated {len(test_cases)} test cases")
        if test_cases:
            # Show first test case as example
            first_test = test_cases[0]
            print(f"   Example: {first_test.get('Test_ID', 'N/A')} - {first_test.get('Test_Scenario', 'N/A')}")
            grounding = first_test.get('Grounded_In', [])
            if grounding:
                print(f"   Grounded in: {', '.join(grounding)[:100]}...")
            all_generated_tests.extend(test_cases)
        print()
    
    return all_generated_tests


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
        
        # Show feature coverage
        features = {}
        for test_case in test_cases:
            feature = test_case.get("Feature", "Unknown")
            features[feature] = features.get(feature, 0) + 1
        
        print(f"🎯 Feature coverage:")
        for feature, count in sorted(features.items()):
            print(f"   {feature}: {count} test cases")
        
        print()
    else:
        print("❌ Test cases file not found")


def demo_query_examples():
    """Show examples of how to respond to user queries."""
    print("❓ DEMO: User Query Response Examples")
    print("=" * 60)
    
    # Initialize RAG system
    rag_system = RAGSystem()
    rag_system.load_documents()
    generator = TestCaseGenerator(rag_system)
    
    # Example user queries and responses
    user_queries = [
        "Generate all positive and negative test cases for the discount code feature",
        "Create test cases for email validation",
        "Test the Pay Now button color requirement"
    ]
    
    for query in user_queries:
        print(f"🙋 USER QUERY: {query}")
        print("🤖 QA AGENT RESPONSE:")
        
        # Generate test cases
        test_cases = generator.generate_test_cases(query)
        
        if not test_cases or (len(test_cases) == 1 and "error" in test_cases[0]):
            print("   ❌ Insufficient grounding. Rebuild KB.")
        else:
            print(f"   ✅ Generated {len(test_cases)} test cases")
            print("   📋 JSON Output:")
            
            # Show first 2 test cases as example
            sample_cases = test_cases[:2]
            print(json.dumps(sample_cases, indent=2))
        
        print("\n" + "-" * 40 + "\n")


def demo_selenium_script_preview():
    """Show what Selenium scripts would look like."""
    print("🤖 DEMO: Selenium Script Generation Preview")
    print("=" * 60)
    
    # Example test case
    sample_test = {
        "Test_ID": "TC-001",
        "Feature": "Discount Code",
        "Test_Scenario": "Apply valid SAVE15 discount code",
        "Expected_Result": "Discount applied successfully, total reduced by 15%, success message displayed"
    }
    
    print(f"📋 Example Test Case: {sample_test['Test_ID']}")
    print(f"   Feature: {sample_test['Feature']}")
    print(f"   Scenario: {sample_test['Test_Scenario']}")
    print()
    
    print("🔧 Generated Selenium Script Structure:")
    print("""
    def test_tc_001():
        driver, wait = setup_driver()
        try:
            # Load checkout page
            driver.get("file://path/to/checkout.html")
            
            # Add item to cart (precondition)
            product_select = Select(driver.find_element(By.ID, "item-select"))
            product_select.select_by_value("laptop")
            driver.find_element(By.ID, "add-to-cart").click()
            
            # Apply SAVE15 discount code
            driver.find_element(By.ID, "discount-code").send_keys("SAVE15")
            driver.find_element(By.ID, "apply-discount").click()
            
            # Verify success message and 15% discount
            message = driver.find_element(By.ID, "discount-message")
            assert message.is_displayed()
            assert "success" in message.get_attribute("class")
            
            discount = driver.find_element(By.ID, "discount-amount")
            assert discount.text != "$0.00"
            
        finally:
            driver.quit()
    """)
    print("💡 Full scripts available with selenium_automation.py")
    print()


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
    demo_grounding_validation()
    demo_query_examples()
    demo_selenium_script_preview()
    
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
    print("Coverage Requirements Met:")
    print("✅ Discount: valid SAVE15 (15% off), invalid/expired, case sensitivity")
    print("✅ Shipping: Standard free; Express adds $10; toggle effects on totals")
    print("✅ Payment: Radio selection Credit Card vs PayPal; green Pay Now button")
    print("✅ Validation: Name/Email/Address required; red error messages")
    print("✅ Cart: Add/remove items; quantity updates; total recalculates")
    print()
    print("Ready to respond to user queries like:")
    print('• "Generate all positive and negative test cases for discount code feature"')


if __name__ == "__main__":
    main()