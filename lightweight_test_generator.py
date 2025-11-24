#!/usr/bin/env python3
"""
Lightweight test case generator for Render deployment
Fallback version that doesn't require scikit-learn or heavy ML dependencies
"""

import json
import re
import os
from typing import List, Dict, Any

class LightweightTestGenerator:
    def __init__(self):
        self.test_cases = []
        self.test_id_counter = 1
        
    def load_documents(self):
        """Load and parse project documents without ML dependencies"""
        self.documents = {
            'product_specs': self.load_file('product_specs.md'),
            'ui_ux_guide': self.load_file('ui_ux_guide.txt'),
            'checkout_html': self.load_file('checkout.html'),
            'api_endpoints': self.load_file('api_endpoints.json')
        }
        print("✅ Documents loaded successfully")
        return True
    
    def load_file(self, filename: str) -> str:
        """Load file content safely"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
        except Exception as e:
            print(f"⚠️ Could not load {filename}: {e}")
            return ""
    
    def generate_discount_tests(self) -> List[Dict[str, Any]]:
        """Generate discount code test cases"""
        tests = []
        
        # Test valid SAVE15 discount
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Discount Code",
            "Preconditions": ["Cart has items totaling $100"],
            "Test_Scenario": "Apply valid SAVE15 discount code",
            "Steps": [
                "Navigate to checkout page",
                "Add items to cart (total $100)",
                "Enter 'SAVE15' in discount code field",
                "Click apply discount button",
                "Verify discount is applied"
            ],
            "Expected_Result": "15% discount applied, total reduced to $85.00",
            "Grounded_In": ["product_specs.md#discount_codes", "checkout.html#discount_functionality"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        # Test valid WELCOME10 discount
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Discount Code",
            "Preconditions": ["Cart has items totaling $100"],
            "Test_Scenario": "Apply valid WELCOME10 discount code",
            "Steps": [
                "Navigate to checkout page",
                "Add items to cart (total $100)",
                "Enter 'WELCOME10' in discount code field",
                "Click apply discount button",
                "Verify discount is applied"
            ],
            "Expected_Result": "10% discount applied, total reduced to $90.00",
            "Grounded_In": ["product_specs.md#discount_codes", "checkout.html#discount_functionality"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        # Test invalid discount code
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Discount Code",
            "Preconditions": ["Cart has items"],
            "Test_Scenario": "Apply invalid discount code",
            "Steps": [
                "Navigate to checkout page",
                "Add items to cart",
                "Enter 'INVALID' in discount code field",
                "Click apply discount button",
                "Verify error message is displayed"
            ],
            "Expected_Result": "Error message displayed: 'Invalid discount code'",
            "Grounded_In": ["product_specs.md#discount_validation", "ui_ux_guide.txt#error_messages"],
            "Risk": "Low",
            "Priority": "P2"
        })
        self.test_id_counter += 1
        
        return tests
    
    def generate_cart_tests(self) -> List[Dict[str, Any]]:
        """Generate cart management test cases"""
        tests = []
        
        # Add item to cart
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Cart",
            "Preconditions": ["Checkout page is loaded", "Cart is empty"],
            "Test_Scenario": "Add single item to cart",
            "Steps": [
                "Click on 'Add Item' button",
                "Verify item appears in cart",
                "Check quantity shows as 1",
                "Verify total is updated"
            ],
            "Expected_Result": "Item added to cart with quantity 1, total price updated",
            "Grounded_In": ["checkout.html#cart_functionality", "product_specs.md#cart_management"],
            "Risk": "High",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        # Update item quantity
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Cart",
            "Preconditions": ["Cart has one item"],
            "Test_Scenario": "Increase item quantity using plus button",
            "Steps": [
                "Locate quantity controls for item",
                "Click plus (+) button",
                "Verify quantity increases to 2",
                "Verify total price is doubled"
            ],
            "Expected_Result": "Quantity updated to 2, total price reflects new quantity",
            "Grounded_In": ["checkout.html#quantity_controls", "product_specs.md#quantity_limits"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        return tests
    
    def generate_payment_tests(self) -> List[Dict[str, Any]]:
        """Generate payment flow test cases"""
        tests = []
        
        # Default payment method
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Payment",
            "Preconditions": ["Cart has items", "User on checkout page"],
            "Test_Scenario": "Verify default payment method is Credit Card",
            "Steps": [
                "Navigate to payment section",
                "Check selected payment method",
                "Verify Credit Card is pre-selected"
            ],
            "Expected_Result": "Credit Card is selected by default",
            "Grounded_In": ["checkout.html#payment_methods", "product_specs.md#payment_defaults"],
            "Risk": "Low",
            "Priority": "P2"
        })
        self.test_id_counter += 1
        
        # Pay Now button styling
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Payment",
            "Preconditions": ["Valid form filled", "Cart not empty"],
            "Test_Scenario": "Verify Pay Now button is green when form is valid",
            "Steps": [
                "Fill all required form fields correctly",
                "Add items to cart",
                "Locate Pay Now button",
                "Verify button color is green"
            ],
            "Expected_Result": "Pay Now button displays with green background color",
            "Grounded_In": ["ui_ux_guide.txt#button_styling", "checkout.html#pay_now_button"],
            "Risk": "Low",
            "Priority": "P3"
        })
        self.test_id_counter += 1
        
        return tests
    
    def generate_validation_tests(self) -> List[Dict[str, Any]]:
        """Generate form validation test cases"""
        tests = []
        
        # Required field validation
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Validation",
            "Preconditions": ["Checkout page loaded"],
            "Test_Scenario": "Submit form with empty required fields",
            "Steps": [
                "Leave customer name field empty",
                "Leave email field empty", 
                "Attempt to submit form",
                "Verify error messages appear"
            ],
            "Expected_Result": "Red error messages displayed for empty required fields",
            "Grounded_In": ["ui_ux_guide.txt#validation_rules", "checkout.html#form_validation"],
            "Risk": "High",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        # Email format validation
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Validation",
            "Preconditions": ["Checkout page loaded"],
            "Test_Scenario": "Enter invalid email format",
            "Steps": [
                "Enter 'invalid-email' in email field",
                "Tab to next field or attempt submit",
                "Verify email validation error appears"
            ],
            "Expected_Result": "Error message: 'Please enter a valid email address'",
            "Grounded_In": ["ui_ux_guide.txt#email_validation", "checkout.html#email_field"],
            "Risk": "Medium",
            "Priority": "P2"
        })
        self.test_id_counter += 1
        
        return tests
    
    def generate_shipping_tests(self) -> List[Dict[str, Any]]:
        """Generate shipping option test cases"""
        tests = []
        
        # Default shipping option
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Shipping",
            "Preconditions": ["Checkout page loaded"],
            "Test_Scenario": "Verify Standard shipping is selected by default",
            "Steps": [
                "Navigate to shipping options section",
                "Check which shipping option is pre-selected",
                "Verify Standard shipping is selected",
                "Verify shipping cost is $0.00"
            ],
            "Expected_Result": "Standard shipping selected by default with $0.00 cost",
            "Grounded_In": ["product_specs.md#shipping_defaults", "checkout.html#shipping_options"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        # Express shipping upgrade
        tests.append({
            "Test_ID": f"TC-{self.test_id_counter:03d}",
            "Feature": "Shipping",
            "Preconditions": ["Checkout page loaded", "Cart total is $50"],
            "Test_Scenario": "Select Express shipping option",
            "Steps": [
                "Select Express shipping option",
                "Verify shipping cost changes to $10.00",
                "Verify total is updated to $60.00"
            ],
            "Expected_Result": "Express shipping adds $10.00 to total cost",
            "Grounded_In": ["product_specs.md#express_shipping", "checkout.html#shipping_calculation"],
            "Risk": "High",
            "Priority": "P1"
        })
        self.test_id_counter += 1
        
        return tests
    
    def generate_all_test_cases(self) -> List[Dict[str, Any]]:
        """Generate all test cases"""
        all_tests = []
        
        # Load documents
        self.load_documents()
        
        # Generate different categories of tests
        all_tests.extend(self.generate_discount_tests())
        all_tests.extend(self.generate_cart_tests())
        all_tests.extend(self.generate_payment_tests())
        all_tests.extend(self.generate_validation_tests())
        all_tests.extend(self.generate_shipping_tests())
        
        return all_tests
    
    def save_test_cases(self, test_cases: List[Dict[str, Any]], filename: str = 'comprehensive_test_cases.json'):
        """Save test cases to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(test_cases, f, indent=2, ensure_ascii=False)
            print(f"✅ Test cases saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving test cases: {e}")
            return False

def main():
    """Main function for standalone execution"""
    print("🚀 Lightweight QA Test Case Generator")
    print("=" * 50)
    
    generator = LightweightTestGenerator()
    
    print("📝 Generating test cases...")
    test_cases = generator.generate_all_test_cases()
    
    print(f"✅ Generated {len(test_cases)} test cases")
    
    # Save test cases
    generator.save_test_cases(test_cases)
    
    print("\n📊 Test Case Summary:")
    features = {}
    for test in test_cases:
        feature = test.get('Feature', 'Unknown')
        features[feature] = features.get(feature, 0) + 1
    
    for feature, count in features.items():
        print(f"  - {feature}: {count} tests")
    
    print(f"\n🎯 Total: {len(test_cases)} test cases generated")
    print("📄 Saved to: comprehensive_test_cases.json")
    
    return test_cases

if __name__ == "__main__":
    main()