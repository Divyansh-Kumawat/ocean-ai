#!/usr/bin/env python3
"""
Demo script to showcase Streamlit QA Agent functionality
Creates sample data and demonstrates the workflow
"""

import json
import os

def create_sample_documents():
    """Create sample documents for demo"""
    
    # Sample product specs
    product_specs = """# E-Shop Checkout Product Specifications

## Discount Codes
- SAVE15: Applies 15% discount to cart total
- WELCOME10: Applies 10% discount to cart total
- Discount codes are case-insensitive
- Only one discount code can be applied at a time

## Cart Management
- Users can add items to cart
- Quantity can be adjusted (1-10 items max)
- Cart total updates in real-time
- Items can be removed from cart

## Shipping Options
- Standard Shipping: Free
- Express Shipping: $10.00 additional cost
- Shipping cost applied after discount

## Payment Methods
- Credit Card (default)
- PayPal
- Pay Now button should be green when form is valid

## Form Validation
- Customer name: Required
- Email: Required, must be valid format
- Address: Required
- Error messages should be displayed in red
"""
    
    # Sample UI/UX guide
    ui_ux_guide = """# UI/UX Guide for E-Shop Checkout

## Color Scheme
- Pay Now button: Green background (#28a745)
- Error messages: Red text (#dc3545)
- Success messages: Green text (#28a745)

## Form Validation Rules
- Real-time validation on field blur
- Error messages appear below fields
- Error messages clear when field is corrected
- Submit button disabled until form is valid

## Button Styling
- Primary buttons: Green background
- Secondary buttons: Gray background
- Hover effects: Darker shade of base color

## Error Handling
- Network errors: Show retry option
- Invalid input: Highlight field in red
- Success states: Show confirmation message
"""

    # Write sample files
    with open('sample_product_specs.md', 'w') as f:
        f.write(product_specs)
    
    with open('sample_ui_ux_guide.txt', 'w') as f:
        f.write(ui_ux_guide)
    
    print("✅ Created sample documents:")
    print("  - sample_product_specs.md")
    print("  - sample_ui_ux_guide.txt")

def create_sample_html():
    """Create sample checkout HTML for demo"""
    
    checkout_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Shop Checkout</title>
    <style>
        .pay-now-btn { background: green; color: white; padding: 10px 20px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <form id="checkout-form">
        <h1>Checkout</h1>
        
        <!-- Customer Information -->
        <div>
            <label for="customer-name">Name:</label>
            <input type="text" id="customer-name" name="customer-name" required>
            <span class="error" id="name-error"></span>
        </div>
        
        <div>
            <label for="customer-email">Email:</label>
            <input type="email" id="customer-email" name="customer-email" required>
            <span class="error" id="email-error"></span>
        </div>
        
        <!-- Cart Section -->
        <div id="cart">
            <h3>Your Cart</h3>
            <div class="cart-item">
                <span>Sample Product</span>
                <input type="number" id="quantity" min="1" max="10" value="1">
                <button type="button" class="add-item">Add Item</button>
            </div>
            <div id="cart-total">Total: $50.00</div>
        </div>
        
        <!-- Discount Code -->
        <div>
            <label for="discount-code">Discount Code:</label>
            <input type="text" id="discount-code" name="discount-code">
            <button type="button" class="apply-discount">Apply</button>
        </div>
        
        <!-- Shipping -->
        <div>
            <h3>Shipping</h3>
            <input type="radio" id="standard" name="shipping" value="standard" checked>
            <label for="standard">Standard (Free)</label>
            
            <input type="radio" id="express" name="shipping" value="express">
            <label for="express">Express ($10.00)</label>
        </div>
        
        <!-- Payment -->
        <div>
            <h3>Payment Method</h3>
            <input type="radio" id="credit-card" name="payment" value="credit-card" checked>
            <label for="credit-card">Credit Card</label>
            
            <input type="radio" id="paypal" name="payment" value="paypal">
            <label for="paypal">PayPal</label>
        </div>
        
        <button type="submit" id="pay-now" class="pay-now-btn">Pay Now</button>
        <div id="success-message" class="success" style="display:none;">Payment Successful!</div>
    </form>
    
    <script>
        // Basic form handling
        document.getElementById('checkout-form').addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('success-message').style.display = 'block';
        });
        
        // Discount code handling
        document.querySelector('.apply-discount').addEventListener('click', function() {
            const code = document.getElementById('discount-code').value.toUpperCase();
            if (code === 'SAVE15' || code === 'WELCOME10') {
                alert('Discount applied!');
            } else {
                alert('Invalid discount code');
            }
        });
    </script>
</body>
</html>"""
    
    with open('sample_checkout.html', 'w') as f:
        f.write(checkout_html)
    
    print("✅ Created sample_checkout.html")

def main():
    """Main demo setup function"""
    print("🌊 Ocean AI QA Agent - Demo Setup")
    print("=" * 40)
    
    print("\n📄 Creating sample documents...")
    create_sample_documents()
    
    print("\n🌐 Creating sample checkout HTML...")
    create_sample_html()
    
    print("\n🎯 Demo Setup Complete!")
    print("\nNext steps:")
    print("1. Run: python launch_streamlit.py")
    print("2. Upload the sample files in Phase 1")
    print("3. Build knowledge base")
    print("4. Generate test cases in Phase 2")
    print("5. Create Selenium scripts in Phase 3")
    
    print("\n📁 Sample files created:")
    print("  - sample_product_specs.md")
    print("  - sample_ui_ux_guide.txt") 
    print("  - sample_checkout.html")

if __name__ == "__main__":
    main()