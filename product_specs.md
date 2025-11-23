# E-Shop Checkout Product Specifications

## Overview
Single-page E-commerce checkout application providing complete order processing functionality including cart management, discount application, shipping selection, payment processing, and order validation.

## Feature Specifications

### 1. Shopping Cart Management

#### Add to Cart Functionality
- **Product Selection**: Dropdown with predefined items (Laptop $999.99, Wireless Mouse $29.99, Mechanical Keyboard $79.99, Gaming Headphones $149.99)
- **Quantity Input**: Numeric input field with min=1, max=10 validation
- **Add Button**: Adds selected product with specified quantity to cart
- **Validation**: Prevents adding items without product selection or invalid quantity

#### Cart Item Management
- **Display**: Shows item name, price, quantity controls, total per item, and remove button
- **Quantity Controls**: Plus/minus buttons and direct input field (1-10 range)
- **Remove Function**: Complete item removal from cart
- **Empty State**: "Your cart is empty" message when no items present
- **Real-time Updates**: Cart totals update immediately on quantity changes

### 2. Discount Code System

#### Valid Discount Codes
- **SAVE15**: Applies 15% discount to subtotal
- **WELCOME10**: Applies 10% discount to subtotal (additional code for testing)

#### Discount Application Rules
- **Case Sensitivity**: Codes are case-insensitive (automatic uppercase conversion)
- **Single Use**: Only one discount code can be applied per order
- **Application**: Applied to subtotal before shipping costs
- **Validation**: Invalid codes show error message "Invalid or expired discount code"
- **Empty Input**: Shows "Please enter a discount code" for empty submissions
- **Success Message**: Displays discount description when successfully applied

#### Edge Cases
- **Whitespace Handling**: Leading/trailing spaces are trimmed
- **Expired Codes**: Any code not in the valid list shows invalid message
- **Multiple Applications**: Subsequent applications replace previous discounts

### 3. Shipping Options

#### Available Methods
- **Standard Shipping**: Free ($0.00)
- **Express Shipping**: Additional $10.00 charge

#### Behavior
- **Default Selection**: Standard shipping is selected by default
- **Real-time Updates**: Total recalculates immediately when shipping method changes
- **Radio Button Group**: Only one shipping method can be selected
- **Cost Application**: Shipping cost added after discount calculation

### 4. Payment Methods

#### Available Options
- **Credit Card**: Default selection
- **PayPal**: Alternative payment method

#### Implementation Notes
- **Selection Required**: One payment method must be selected for form validation
- **UI Display**: Radio button group with clear labels
- **Form Integration**: Payment selection affects form validation state

### 5. Form Validation

#### Required Fields
- **Full Name**: Text input, required, cannot be empty or whitespace only
- **Email Address**: Email input with format validation (pattern: email@domain.com)
- **Address**: Text input, required, cannot be empty or whitespace only

#### Validation Behavior
- **Real-time Validation**: Errors appear as user types or leaves field
- **Error Display**: Red text error messages below each field
- **Error Clearing**: Errors disappear when user corrects input or focuses on field
- **Submit Prevention**: Pay Now button disabled until all validations pass

#### Error Messages
- **Name Error**: "Full name is required"
- **Email Error**: "Valid email address is required"
- **Address Error**: "Address is required"

### 6. Order Processing

#### Pay Now Button
- **Color**: Green background (RGB: green)
- **State Management**: Disabled when form invalid or cart empty
- **Hover Effect**: Darker green on hover
- **Success Behavior**: Shows "Payment Successful!" message

#### Success Flow
- **Message Display**: "Payment Successful!" in green success box
- **Page Replacement**: Entire form replaced with success message
- **Additional Content**: Thank you message and email confirmation notice

### 7. Calculation Logic

#### Price Calculations
1. **Subtotal**: Sum of all cart items (quantity × price)
2. **Discount**: Percentage applied to subtotal (15% for SAVE15)
3. **Shipping**: Added after discount ($0 for Standard, $10 for Express)
4. **Final Total**: (Subtotal - Discount) + Shipping

#### Display Format
- **Currency**: US Dollar ($) format with 2 decimal places
- **Negative Discounts**: Shown as "-$X.XX" for clarity
- **Zero Values**: Displayed as "$0.00"

## Technical Requirements

### HTML Structure
- **Semantic HTML**: Proper form elements and labels
- **Accessibility**: All inputs have associated labels
- **ID Management**: Stable selectors for testing automation

### JavaScript Functionality
- **Event Driven**: Real-time updates and validation
- **State Management**: Global cart and discount state
- **Error Handling**: Graceful handling of edge cases

### CSS Styling
- **Responsive Design**: Centered layout with mobile considerations
- **Visual Feedback**: Clear error states and interactive elements
- **Consistent Theming**: Professional e-commerce appearance

## Browser Requirements
- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **JavaScript Enabled**: Required for full functionality
- **No External Dependencies**: Self-contained HTML file