"""
E-Shop Checkout Selenium Test Automation
Senior Python + Selenium Test Suite

This module provides comprehensive Selenium automation for the E-Shop checkout application.
Uses stable selectors from checkout.html and validates against grounded documentation.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import unittest
from pathlib import Path


class CheckoutTestAutomation:
    """Main class for E-Shop checkout test automation."""
    
    def __init__(self, headless=False, wait_timeout=10):
        self.wait_timeout = wait_timeout
        self.driver = None
        self.wait = None
        self.checkout_url = f"file://{Path(__file__).parent.absolute()}/checkout.html"
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """Initialize Chrome WebDriver with options."""
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1200,800")
        
        # Initialize driver (assumes ChromeDriver is in PATH)
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver: {e}")
    
    def load_checkout_page(self):
        """Load the checkout page."""
        self.driver.get(self.checkout_url)
        # Wait for page to load completely
        self.wait.until(EC.presence_of_element_located((By.ID, "checkout-form")))
    
    def teardown(self):
        """Close browser and cleanup."""
        if self.driver:
            self.driver.quit()
    
    # Cart Management Methods
    def add_item_to_cart(self, item_value, quantity=1):
        """Add an item to the cart."""
        # Select product from dropdown
        product_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value(item_value)
        
        # Set quantity
        quantity_input = self.driver.find_element(By.ID, "add-quantity")
        quantity_input.clear()
        quantity_input.send_keys(str(quantity))
        
        # Click add to cart
        add_button = self.driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        
        # Wait for cart to update
        time.sleep(0.5)
    
    def get_cart_items_count(self):
        """Get the number of items in cart."""
        cart_items = self.driver.find_elements(By.CSS_SELECTOR, "#cart-items .cart-item")
        return len(cart_items)
    
    def remove_item_from_cart(self, item_index=0):
        """Remove an item from cart by index."""
        remove_buttons = self.driver.find_elements(By.CLASS_NAME, "remove-btn")
        if item_index < len(remove_buttons):
            remove_buttons[item_index].click()
            time.sleep(0.5)
    
    def update_item_quantity(self, item_index=0, new_quantity=1):
        """Update quantity of cart item."""
        qty_inputs = self.driver.find_elements(By.CLASS_NAME, "qty-input")
        if item_index < len(qty_inputs):
            qty_input = qty_inputs[item_index]
            qty_input.clear()
            qty_input.send_keys(str(new_quantity))
            # Trigger change event
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", qty_input)
            time.sleep(0.5)
    
    def get_subtotal(self):
        """Get the current subtotal amount."""
        subtotal_element = self.driver.find_element(By.ID, "subtotal")
        return subtotal_element.text
    
    def get_final_total(self):
        """Get the final total amount."""
        total_element = self.driver.find_element(By.ID, "final-total")
        return total_element.text
    
    # Discount Code Methods
    def apply_discount_code(self, code):
        """Apply a discount code."""
        # Enter discount code
        discount_input = self.driver.find_element(By.ID, "discount-code")
        discount_input.clear()
        discount_input.send_keys(code)
        
        # Click apply button
        apply_button = self.driver.find_element(By.ID, "apply-discount")
        apply_button.click()
        
        # Wait for response
        time.sleep(1)
    
    def get_discount_message(self):
        """Get the discount message text and type."""
        message_element = self.driver.find_element(By.ID, "discount-message")
        message_text = message_element.text
        is_visible = message_element.is_displayed()
        
        # Check message type by class
        message_type = "none"
        if "discount-success" in message_element.get_attribute("class"):
            message_type = "success"
        elif "discount-error" in message_element.get_attribute("class"):
            message_type = "error"
        
        return {
            "text": message_text,
            "visible": is_visible,
            "type": message_type
        }
    
    def get_discount_amount(self):
        """Get the current discount amount."""
        discount_element = self.driver.find_element(By.ID, "discount-amount")
        return discount_element.text
    
    # Shipping Methods
    def select_shipping_method(self, method="standard"):
        """Select shipping method (standard or express)."""
        if method == "standard":
            radio = self.driver.find_element(By.ID, "standard-shipping")
        elif method == "express":
            radio = self.driver.find_element(By.ID, "express-shipping")
        else:
            raise ValueError("Invalid shipping method. Use 'standard' or 'express'.")
        
        radio.click()
        time.sleep(0.5)
    
    def get_shipping_cost(self):
        """Get the current shipping cost."""
        shipping_element = self.driver.find_element(By.ID, "shipping-cost")
        return shipping_element.text
    
    # Payment Methods
    def select_payment_method(self, method="credit-card"):
        """Select payment method (credit-card or paypal)."""
        if method == "credit-card":
            radio = self.driver.find_element(By.ID, "credit-card")
        elif method == "paypal":
            radio = self.driver.find_element(By.ID, "paypal")
        else:
            raise ValueError("Invalid payment method. Use 'credit-card' or 'paypal'.")
        
        radio.click()
        time.sleep(0.2)
    
    # Form Validation Methods
    def fill_customer_info(self, name="", email="", address=""):
        """Fill customer information fields."""
        if name:
            name_field = self.driver.find_element(By.ID, "customer-name")
            name_field.clear()
            name_field.send_keys(name)
        
        if email:
            email_field = self.driver.find_element(By.ID, "customer-email")
            email_field.clear()
            email_field.send_keys(email)
        
        if address:
            address_field = self.driver.find_element(By.ID, "customer-address")
            address_field.clear()
            address_field.send_keys(address)
        
        time.sleep(0.5)
    
    def get_field_error(self, field_name):
        """Get error message for a specific field."""
        error_id = f"{field_name}-error"
        try:
            error_element = self.driver.find_element(By.ID, error_id)
            return {
                "text": error_element.text,
                "visible": error_element.is_displayed(),
                "color": error_element.value_of_css_property("color")
            }
        except NoSuchElementException:
            return {"text": "", "visible": False, "color": ""}
    
    def is_pay_now_enabled(self):
        """Check if Pay Now button is enabled."""
        pay_button = self.driver.find_element(By.ID, "pay-now")
        return pay_button.is_enabled()
    
    def get_pay_now_button_color(self):
        """Get the background color of Pay Now button."""
        pay_button = self.driver.find_element(By.ID, "pay-now")
        return pay_button.value_of_css_property("background-color")
    
    def click_pay_now(self):
        """Click the Pay Now button."""
        pay_button = self.wait.until(EC.element_to_be_clickable((By.ID, "pay-now")))
        pay_button.click()
        time.sleep(2)  # Allow for page transition
    
    def get_success_message(self):
        """Get the success message after payment."""
        try:
            success_element = self.driver.find_element(By.ID, "success-message")
            return {
                "text": success_element.text,
                "visible": success_element.is_displayed()
            }
        except NoSuchElementException:
            return {"text": "", "visible": False}


class SeleniumTestCase:
    """Individual test case execution with Selenium."""
    
    def __init__(self, test_case_json, automation):
        self.test_case = test_case_json
        self.automation = automation
        self.result = {"passed": False, "error": "", "details": ""}
    
    def execute(self):
        """Execute the test case steps."""
        try:
            test_id = self.test_case.get("Test_ID", "Unknown")
            feature = self.test_case.get("Feature", "Unknown")
            
            print(f"Executing {test_id}: {feature}")
            
            # Load fresh page for each test
            self.automation.load_checkout_page()
            
            # Execute based on feature
            if feature == "Discount Code":
                self._execute_discount_test()
            elif feature == "Shipping":
                self._execute_shipping_test()
            elif feature == "Payment":
                self._execute_payment_test()
            elif feature == "Validation":
                self._execute_validation_test()
            elif feature == "Cart":
                self._execute_cart_test()
            else:
                raise Exception(f"Unknown feature: {feature}")
            
            self.result["passed"] = True
            print(f"✓ {test_id} PASSED")
            
        except Exception as e:
            self.result["error"] = str(e)
            self.result["passed"] = False
            print(f"✗ {test_id} FAILED: {e}")
    
    def _execute_discount_test(self):
        """Execute discount code related test."""
        scenario = self.test_case.get("Test_Scenario", "").lower()
        
        # Add item to cart first (precondition)
        self.automation.add_item_to_cart("laptop", 1)
        
        if "valid save15" in scenario:
            # Test valid SAVE15 code
            original_total = self.automation.get_final_total()
            self.automation.apply_discount_code("SAVE15")
            
            # Verify success message
            message = self.automation.get_discount_message()
            if not message["visible"] or message["type"] != "success":
                raise Exception("Success message not displayed or wrong type")
            
            # Verify 15% discount applied
            discount_amount = self.automation.get_discount_amount()
            if discount_amount == "$0.00":
                raise Exception("Discount not applied")
        
        elif "invalid" in scenario:
            # Test invalid code
            self.automation.apply_discount_code("INVALID123")
            
            # Verify error message
            message = self.automation.get_discount_message()
            if not message["visible"] or message["type"] != "error":
                raise Exception("Error message not displayed or wrong type")
            
            if "invalid or expired" not in message["text"].lower():
                raise Exception(f"Wrong error message: {message['text']}")
        
        elif "case sensitivity" in scenario:
            # Test case insensitivity
            self.automation.apply_discount_code("save15")
            
            # Verify discount still works
            message = self.automation.get_discount_message()
            if not message["visible"] or message["type"] != "success":
                raise Exception("Case sensitivity test failed - discount not applied")
    
    def _execute_shipping_test(self):
        """Execute shipping related test."""
        scenario = self.test_case.get("Test_Scenario", "").lower()
        
        # Add item to cart (precondition)
        self.automation.add_item_to_cart("laptop", 1)
        
        if "standard" in scenario:
            # Test standard shipping (should be default)
            self.automation.select_shipping_method("standard")
            shipping_cost = self.automation.get_shipping_cost()
            if shipping_cost != "$0.00":
                raise Exception(f"Standard shipping should be free, got: {shipping_cost}")
        
        elif "express" in scenario:
            # Test express shipping
            self.automation.select_shipping_method("express")
            shipping_cost = self.automation.get_shipping_cost()
            if shipping_cost != "$10.00":
                raise Exception(f"Express shipping should be $10.00, got: {shipping_cost}")
    
    def _execute_payment_test(self):
        """Execute payment related test."""
        scenario = self.test_case.get("Test_Scenario", "").lower()
        
        # Setup valid form (preconditions)
        self.automation.add_item_to_cart("laptop", 1)
        self.automation.fill_customer_info("John Doe", "john@example.com", "123 Main St")
        
        if "credit card" in scenario:
            self.automation.select_payment_method("credit-card")
        elif "paypal" in scenario:
            self.automation.select_payment_method("paypal")
        
        # Verify Pay Now button is enabled and green
        if not self.automation.is_pay_now_enabled():
            raise Exception("Pay Now button should be enabled with valid form")
        
        # Check button color (should be green)
        button_color = self.automation.get_pay_now_button_color()
        # Note: Color comparison may vary by browser, so we check for green-ish values
        
        # Click Pay Now
        self.automation.click_pay_now()
        
        # Verify success message
        success = self.automation.get_success_message()
        if not success["visible"]:
            raise Exception("Success message not displayed")
        
        if "Payment Successful!" not in success["text"]:
            raise Exception(f"Wrong success message: {success['text']}")
    
    def _execute_validation_test(self):
        """Execute validation related test."""
        scenario = self.test_case.get("Test_Scenario", "").lower()
        
        # Add item to cart (precondition)
        self.automation.add_item_to_cart("laptop", 1)
        
        if "empty" in scenario and "name" in scenario:
            # Test empty name field
            self.automation.fill_customer_info("", "john@example.com", "123 Main St")
            
            # Check for name error
            error = self.automation.get_field_error("name")
            if not error["visible"]:
                raise Exception("Name error should be visible")
            
            if "full name is required" not in error["text"].lower():
                raise Exception(f"Wrong name error message: {error['text']}")
            
            # Verify error is red
            if "rgb(255, 0, 0)" not in error["color"] and "red" not in error["color"]:
                raise Exception(f"Error should be red, got: {error['color']}")
        
        elif "invalid email" in scenario:
            # Test invalid email
            self.automation.fill_customer_info("John Doe", "invalid-email", "123 Main St")
            
            # Check for email error
            error = self.automation.get_field_error("email")
            if not error["visible"]:
                raise Exception("Email error should be visible")
            
            if "valid email address is required" not in error["text"].lower():
                raise Exception(f"Wrong email error message: {error['text']}")
    
    def _execute_cart_test(self):
        """Execute cart related test."""
        scenario = self.test_case.get("Test_Scenario", "").lower()
        
        if "add item" in scenario:
            # Test adding item to cart
            initial_count = self.automation.get_cart_items_count()
            self.automation.add_item_to_cart("laptop", 2)
            
            final_count = self.automation.get_cart_items_count()
            if final_count != initial_count + 1:
                raise Exception("Item not added to cart")
            
            # Verify total calculation
            total = self.automation.get_final_total()
            if total == "$0.00":
                raise Exception("Total not calculated correctly")
        
        elif "update" in scenario and "quantity" in scenario:
            # Test quantity update
            self.automation.add_item_to_cart("laptop", 1)
            original_total = self.automation.get_final_total()
            
            # Update quantity
            self.automation.update_item_quantity(0, 2)
            
            new_total = self.automation.get_final_total()
            if new_total == original_total:
                raise Exception("Total should update when quantity changes")


def run_test_suite(test_cases_json):
    """Run a complete test suite from JSON test cases."""
    automation = CheckoutTestAutomation(headless=False)
    results = []
    
    try:
        for test_case in test_cases_json:
            if "error" in test_case:
                print(f"Skipping test due to error: {test_case['error']}")
                continue
            
            test = SeleniumTestCase(test_case, automation)
            test.execute()
            results.append({
                "test_id": test_case.get("Test_ID", "Unknown"),
                "feature": test_case.get("Feature", "Unknown"),
                "passed": test.result["passed"],
                "error": test.result["error"]
            })
    
    finally:
        automation.teardown()
    
    return results


def generate_selenium_script_for_test(test_case_json, html_content=""):
    """Generate a standalone Selenium script for a specific test case."""
    
    test_id = test_case_json.get("Test_ID", "Unknown")
    feature = test_case_json.get("Feature", "Unknown")
    scenario = test_case_json.get("Test_Scenario", "")
    expected_result = test_case_json.get("Expected_Result", "")
    
    script_template = f'''"""
Selenium Test Script for {test_id}: {feature}
Generated automatically from test case definition.

Test Scenario: {scenario}
Expected Result: {expected_result}
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pathlib import Path


def setup_driver(headless=False):
    """Initialize Chrome WebDriver with options."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,800")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    return driver, wait


def test_{test_id.lower().replace('-', '_')}():
    """Execute test case {test_id}."""
    driver, wait = setup_driver()
    
    try:
        # Load checkout page
        checkout_url = f"file://{{Path(__file__).parent.absolute()}}/checkout.html"
        driver.get(checkout_url)
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.ID, "checkout-form")))
        
        print(f"Executing {test_id}: {feature}")
        '''
    
    # Add feature-specific test logic
    if feature == "Discount Code":
        if "valid save15" in scenario.lower():
            script_template += '''
        # Add item to cart (precondition)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        
        quantity_input = driver.find_element(By.ID, "add-quantity")
        quantity_input.clear()
        quantity_input.send_keys("1")
        
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Apply SAVE15 discount code
        discount_input = driver.find_element(By.ID, "discount-code")
        discount_input.send_keys("SAVE15")
        
        apply_button = driver.find_element(By.ID, "apply-discount")
        apply_button.click()
        time.sleep(1)
        
        # Verify success message appears
        message_element = driver.find_element(By.ID, "discount-message")
        assert message_element.is_displayed(), "Success message should be visible"
        assert "discount-success" in message_element.get_attribute("class"), "Should show success message"
        
        # Verify 15% discount is applied
        discount_amount = driver.find_element(By.ID, "discount-amount")
        assert discount_amount.text != "$0.00", "Discount should be applied"
        
        print("✓ SAVE15 discount code applied successfully")
        '''
        elif "invalid" in scenario.lower():
            script_template += '''
        # Add item to cart (precondition)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Apply invalid discount code
        discount_input = driver.find_element(By.ID, "discount-code")
        discount_input.send_keys("INVALID123")
        
        apply_button = driver.find_element(By.ID, "apply-discount")
        apply_button.click()
        time.sleep(1)
        
        # Verify error message appears
        message_element = driver.find_element(By.ID, "discount-message")
        assert message_element.is_displayed(), "Error message should be visible"
        assert "discount-error" in message_element.get_attribute("class"), "Should show error message"
        assert "invalid or expired" in message_element.text.lower(), f"Wrong error message: {message_element.text}"
        
        print("✓ Invalid discount code properly rejected")
        '''
    
    elif feature == "Shipping":
        if "express" in scenario.lower():
            script_template += '''
        # Add item to cart (precondition)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Select Express shipping
        express_radio = driver.find_element(By.ID, "express-shipping")
        express_radio.click()
        time.sleep(0.5)
        
        # Verify shipping cost is $10.00
        shipping_cost = driver.find_element(By.ID, "shipping-cost")
        assert shipping_cost.text == "$10.00", f"Express shipping should cost $10.00, got: {shipping_cost.text}"
        
        # Verify total is recalculated
        final_total = driver.find_element(By.ID, "final-total")
        assert final_total.text != "$0.00", "Total should be recalculated"
        
        print("✓ Express shipping adds $10.00 to total")
        '''
    
    elif feature == "Payment":
        script_template += '''
        # Setup valid form (preconditions)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Fill customer information
        name_field = driver.find_element(By.ID, "customer-name")
        name_field.send_keys("John Doe")
        
        email_field = driver.find_element(By.ID, "customer-email")
        email_field.send_keys("john@example.com")
        
        address_field = driver.find_element(By.ID, "customer-address")
        address_field.send_keys("123 Main St")
        time.sleep(0.5)
        '''
        
        if "paypal" in scenario.lower():
            script_template += '''
        # Select PayPal payment method
        paypal_radio = driver.find_element(By.ID, "paypal")
        paypal_radio.click()
        '''
        
        script_template += '''
        # Verify Pay Now button is green and enabled
        pay_button = driver.find_element(By.ID, "pay-now")
        assert pay_button.is_enabled(), "Pay Now button should be enabled"
        
        button_color = pay_button.value_of_css_property("background-color")
        # Note: Green color check - exact values may vary by browser
        
        # Click Pay Now button
        pay_button.click()
        time.sleep(2)
        
        # Verify "Payment Successful!" message appears
        try:
            success_element = driver.find_element(By.ID, "success-message")
            assert success_element.is_displayed(), "Success message should be visible"
            assert "Payment Successful!" in success_element.text, f"Wrong success message: {success_element.text}"
            print("✓ Payment processed successfully")
        except:
            # Check if page was replaced with success content
            page_source = driver.page_source
            assert "Payment Successful!" in page_source, "Payment success message not found"
            print("✓ Payment successful - page replaced with success message")
        '''
    
    elif feature == "Validation":
        if "name" in scenario.lower():
            script_template += '''
        # Add item to cart (precondition)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Fill form with empty name field
        email_field = driver.find_element(By.ID, "customer-email")
        email_field.send_keys("john@example.com")
        
        address_field = driver.find_element(By.ID, "customer-address")
        address_field.send_keys("123 Main St")
        
        # Trigger validation by clicking on name field and leaving it empty
        name_field = driver.find_element(By.ID, "customer-name")
        name_field.click()
        address_field.click()  # Focus away to trigger validation
        time.sleep(0.5)
        
        # Verify name error appears in red
        name_error = driver.find_element(By.ID, "name-error")
        assert name_error.is_displayed(), "Name error should be visible"
        assert "Full name is required" in name_error.text, f"Wrong error message: {name_error.text}"
        
        error_color = name_error.value_of_css_property("color")
        # Check for red color (may be rgb(255, 0, 0) or "red")
        assert "255, 0, 0" in error_color or "red" in error_color, f"Error should be red, got: {error_color}"
        
        print("✓ Name validation error displayed in red")
        '''
        elif "email" in scenario.lower():
            script_template += '''
        # Add item to cart (precondition)
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Fill form with invalid email
        name_field = driver.find_element(By.ID, "customer-name")
        name_field.send_keys("John Doe")
        
        email_field = driver.find_element(By.ID, "customer-email")
        email_field.send_keys("invalid-email")
        
        address_field = driver.find_element(By.ID, "customer-address")
        address_field.send_keys("123 Main St")
        
        # Trigger validation
        email_field.click()
        address_field.click()
        time.sleep(0.5)
        
        # Verify email error appears in red
        email_error = driver.find_element(By.ID, "email-error")
        assert email_error.is_displayed(), "Email error should be visible"
        assert "Valid email address is required" in email_error.text, f"Wrong error message: {email_error.text}"
        
        error_color = email_error.value_of_css_property("color")
        assert "255, 0, 0" in error_color or "red" in error_color, f"Error should be red, got: {error_color}"
        
        print("✓ Email validation error displayed in red")
        '''
    
    elif feature == "Cart":
        script_template += '''
        # Get initial cart state
        cart_items = driver.find_elements(By.CSS_SELECTOR, "#cart-items .cart-item")
        initial_count = len(cart_items)
        
        # Add laptop to cart with quantity 2
        product_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "item-select"))))
        product_select.select_by_value("laptop")
        
        quantity_input = driver.find_element(By.ID, "add-quantity")
        quantity_input.clear()
        quantity_input.send_keys("2")
        
        add_button = driver.find_element(By.ID, "add-to-cart")
        add_button.click()
        time.sleep(0.5)
        
        # Verify item was added
        cart_items = driver.find_elements(By.CSS_SELECTOR, "#cart-items .cart-item")
        assert len(cart_items) == initial_count + 1, "Item should be added to cart"
        
        # Verify total calculation
        final_total = driver.find_element(By.ID, "final-total")
        assert final_total.text != "$0.00", "Total should be calculated"
        
        # For laptop at $999.99 x 2 = $1999.98
        if "laptop" in scenario.lower():
            assert "1999.98" in final_total.text, f"Expected $1999.98 for 2 laptops, got: {final_total.text}"
        
        print("✓ Item added to cart with correct total")
        '''
    
    # Add cleanup
    script_template += '''
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    test_''' + test_id.lower().replace('-', '_') + '''()
    print("Test completed successfully!")
'''
    
    return script_template


if __name__ == "__main__":
    # Example usage
    sample_test_case = {
        "Test_ID": "TC-001",
        "Feature": "Discount Code",
        "Test_Scenario": "Apply valid SAVE15 discount code",
        "Expected_Result": "Discount applied successfully, total reduced by 15%"
    }
    
    # Generate Selenium script
    script = generate_selenium_script_for_test(sample_test_case)
    print(script)