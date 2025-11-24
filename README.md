# E-Shop Checkout QA Testing Framework

This directory contains a comprehensive testing framework for the E-Shop Checkout application, built according to autonomous QA lead requirements with strict grounding in provided context.

## Project Structure

```
oceanai-assignment/
├── checkout.html              # Single-page E-Shop checkout application
├── product_specs.md          # Complete functional requirements
├── ui_ux_guide.txt           # UI/UX specifications and styling rules
├── api_endpoints.json        # Optional API endpoint definitions
├── test_case_generator.py    # RAG system for test case generation
├── selenium_automation.py    # Selenium test automation framework
├── comprehensive_test_cases.json # Complete test suite (30 test cases)
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Key Features

### 1. E-Shop Checkout Application (checkout.html)
- **Cart Management**: Add/remove items, update quantities, real-time totals
- **Discount Codes**: SAVE15 (15% off), WELCOME10 (10% off), case-insensitive
- **Shipping Options**: Standard (free), Express (+$10)
- **Payment Methods**: Credit Card (default), PayPal
- **Form Validation**: Real-time validation with red error messages
- **Success Flow**: "Payment Successful!" message after valid form submission

### 2. Stable Selectors for Testing
The HTML uses consistent, testable selectors:
- **IDs**: `discount-code`, `pay-now`, `customer-name`, `customer-email`, etc.
- **Names**: Form elements have matching name attributes
- **CSS Classes**: Consistent styling classes for reliable selection

### 3. RAG-Based Test Case Generation
The `test_case_generator.py` implements:
- **Document Parsing**: Automated extraction from specs, HTML, and guides
- **Contextual Retrieval**: Semantic search for relevant documentation chunks
- **Grounded Test Cases**: Every test case cites exact source documents
- **JSON Schema Compliance**: Strict adherence to specified test case format

### 4. Comprehensive Test Coverage
30 test cases covering:
- **Positive Scenarios**: Valid inputs and expected workflows
- **Negative Scenarios**: Invalid inputs and error handling
- **Boundary Testing**: Edge cases and limits (quantity 1-10, etc.)
- **Integration Testing**: Multiple feature interactions

## Test Case Categories

### Discount Code Testing (TC-001 to TC-005, TC-027, TC-030)
- Valid SAVE15 code application
- Invalid code rejection
- Case sensitivity handling
- Empty code validation
- Whitespace trimming
- Multiple discount scenarios
- Discount with shipping interaction

### Shipping Testing (TC-006 to TC-008)
- Default Standard shipping (free)
- Express shipping cost addition
- Shipping method changes with discounts

### Payment Testing (TC-009 to TC-011, TC-026)
- Default Credit Card selection
- PayPal method selection
- Pay Now button styling (green requirement)
- Complete payment flow with success message

### Form Validation Testing (TC-012 to TC-015, TC-025, TC-029)
- Required field validation (name, email, address)
- Email format validation
- Error message styling (red requirement)
- Error clearing on correction
- Empty cart validation

### Cart Management Testing (TC-016 to TC-024, TC-028)
- Single and multiple item addition
- Quantity controls (plus/minus buttons)
- Direct quantity input
- Item removal
- Empty cart state
- Boundary value testing (1-10 quantity)
- Duplicate item handling

## Grounding and Citations

Every test case includes `"Grounded_In"` references citing:
- **product_specs.md**: Functional requirements and business rules
- **ui_ux_guide.txt**: UI specifications and styling requirements
- **checkout.html**: HTML structure and element selectors
- **api_endpoints.json**: Optional API integration points

Example grounding:
```json
"Grounded_In": [
  "product_specs.md#discount_application_rules",
  "ui_ux_guide.txt#error_handling_specifications",
  "checkout.html#element_ids"
]
```

## Running the Tests

### Prerequisites
1. Python 3.8+
2. Chrome browser installed
3. ChromeDriver in PATH or use webdriver-manager

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# For automatic ChromeDriver management, install webdriver-manager
pip install webdriver-manager
```

### 🌊 Run Streamlit QA Agent (NEW!)
```bash
# Install Streamlit dependencies
pip install -r requirements-streamlit.txt

# Launch the autonomous QA agent interface
streamlit run streamlit_app.py

# Open your browser to: http://localhost:8501
```

**Streamlit App Features:**
- **Phase 1**: Upload documents and build knowledge base
- **Phase 2**: Generate test cases using AI agent
- **Phase 3**: Create Selenium scripts automatically

### Generate Test Cases
```bash
# Run RAG system to generate test cases
python3 test_case_generator.py

# Or generate for specific features
python3 -c "
from test_case_generator import RAGSystem, TestCaseGenerator
rag = RAGSystem()
rag.load_documents()
generator = TestCaseGenerator(rag)
cases = generator.generate_test_cases('Generate discount code test cases')
import json
print(json.dumps(cases, indent=2))
"
```

### Run Selenium Tests
```bash
# Run individual test case
python3 selenium_automation.py

# Or run specific test from JSON
python3 -c "
import json
from selenium_automation import SeleniumTestCase, CheckoutTestAutomation

with open('comprehensive_test_cases.json', 'r') as f:
    test_cases = json.load(f)

automation = CheckoutTestAutomation()
for test_case in test_cases[:5]:  # Run first 5 tests
    test = SeleniumTestCase(test_case, automation)
    test.execute()
automation.teardown()
"
```

### Generate Selenium Script for Specific Test
```bash
python3 -c "
import json
from selenium_automation import generate_selenium_script_for_test

with open('comprehensive_test_cases.json', 'r') as f:
    test_cases = json.load(f)

# Generate script for discount code test
script = generate_selenium_script_for_test(test_cases[0])
print(script)
"
```

## Test Case Schema

Each test case follows the strict JSON schema:
```json
{
  "Test_ID": "TC-XXX",
  "Feature": "Discount Code | Shipping | Payment | Validation | Cart",
  "Preconditions": ["Requirement 1", "Requirement 2"],
  "Test_Scenario": "Brief description of test scenario",
  "Steps": ["Step 1", "Step 2", "Step 3"],
  "Expected_Result": "Observable outcome description",
  "Grounded_In": ["source_document#section", "another_source"],
  "Risk": "Low|Medium|High",
  "Priority": "P1|P2|P3"
}
```

## Key Requirements Compliance

### UI/UX Requirements
- ✅ Pay Now button is green (CSS: `background: green`)
- ✅ Error messages displayed in red text
- ✅ Success message: "Payment Successful!" (exact text)
- ✅ Form validation with real-time error clearing

### Functional Requirements
- ✅ SAVE15 applies exactly 15% discount
- ✅ Express shipping adds exactly $10.00
- ✅ Case-insensitive discount codes
- ✅ Calculation order: (Subtotal - Discount) + Shipping
- ✅ Quantity range validation (1-10)

### Testing Requirements
- ✅ Stable selectors (IDs preferred, then names, then CSS)
- ✅ No brittle XPaths used
- ✅ Comprehensive coverage (positive, negative, boundary, edge cases)
- ✅ Strict grounding in provided documentation
- ✅ JSON schema compliance

## Error Handling

If selector not found in HTML:
```
"Selector not found in HTML: #missing-element"
```

If insufficient grounding:
```
"Insufficient grounding. Rebuild KB."
```

If requirement not specified:
```
"Not specified"
```

## Browser Compatibility

Tests designed for:
- Chrome (primary)
- Firefox (compatible)
- Safari (compatible)
- Edge (compatible)

All tests use WebDriverWait for reliable element interaction and avoid flaky time.sleep() calls where possible.

## Validation Rules Summary

1. **Discount Codes**: SAVE15 (15% off), case-insensitive, one at a time
2. **Shipping**: Standard free, Express +$10, applied after discount
3. **Cart**: Quantity 1-10, real-time updates, duplicate item handling
4. **Form**: Name/Email/Address required, email format validation
5. **Payment**: Green Pay Now button, disabled until valid form + non-empty cart
6. **Success**: Exact text "Payment Successful!" required

This framework provides complete autonomous QA capabilities with strict adherence to provided specifications and comprehensive test coverage.# ocean-ai
# ocean-ai
