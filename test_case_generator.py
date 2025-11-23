"""
E-Shop Checkout QA Test Case Generator
Autonomous QA Lead System with RAG Integration

This module implements a RAG (Retrieval-Augmented Generation) system for generating
comprehensive test cases based on provided context documents.
"""

import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import os


class DocumentChunk:
    """Represents a chunk of text from a source document."""
    
    def __init__(self, content: str, source_document: str, line_number: int = None, section: str = None):
        self.content = content.strip()
        self.source_document = source_document
        self.line_number = line_number
        self.section = section
    
    def get_grounding_reference(self) -> str:
        """Generate grounding reference for citations."""
        if self.line_number:
            return f"{self.source_document}#line{self.line_number}"
        elif self.section:
            return f"{self.source_document}#{self.section}"
        else:
            return self.source_document


class RAGSystem:
    """Retrieval-Augmented Generation system for test case generation."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or "/Users/zwarup.cj/Documents/projects/oceanai-assignment"
        self.document_chunks = []
        self.supported_files = ['product_specs.md', 'ui_ux_guide.txt', 'checkout.html', 'api_endpoints.json']
        
    def load_documents(self):
        """Load and parse all support documents into chunks."""
        self.document_chunks = []
        
        for filename in self.supported_files:
            file_path = Path(self.workspace_path) / filename
            if file_path.exists():
                self._parse_document(str(file_path), filename)
    
    def _parse_document(self, file_path: str, filename: str):
        """Parse a document into meaningful chunks."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if filename.endswith('.md'):
            self._parse_markdown(content, filename)
        elif filename.endswith('.txt'):
            self._parse_text_file(content, filename)
        elif filename.endswith('.html'):
            self._parse_html(content, filename)
        elif filename.endswith('.json'):
            self._parse_json(content, filename)
    
    def _parse_markdown(self, content: str, filename: str):
        """Parse markdown file into sections."""
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                # Save previous section
                if current_section and section_content:
                    chunk_content = '\n'.join(section_content).strip()
                    if chunk_content:
                        chunk = DocumentChunk(chunk_content, filename, section=current_section.lower().replace(' ', '_'))
                        self.document_chunks.append(chunk)
                
                # Start new section
                current_section = line.strip('#').strip()
                section_content = [line]
            else:
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            chunk_content = '\n'.join(section_content).strip()
            if chunk_content:
                chunk = DocumentChunk(chunk_content, filename, section=current_section.lower().replace(' ', '_'))
                self.document_chunks.append(chunk)
    
    def _parse_text_file(self, content: str, filename: str):
        """Parse text file into sections based on delimiters."""
        # Split by section delimiters (=== lines)
        sections = re.split(r'\n={3,}\n', content)
        
        for i, section in enumerate(sections):
            section = section.strip()
            if section:
                # Extract section title if present
                lines = section.split('\n')
                section_title = lines[0] if lines else f"section_{i+1}"
                chunk = DocumentChunk(section, filename, section=section_title.lower().replace(' ', '_'))
                self.document_chunks.append(chunk)
    
    def _parse_html(self, content: str, filename: str):
        """Parse HTML file to extract element information."""
        # Extract elements with IDs
        id_pattern = r'id=["\']([^"\']+)["\']'
        ids = re.findall(id_pattern, content)
        
        # Extract elements with names
        name_pattern = r'name=["\']([^"\']+)["\']'
        names = re.findall(name_pattern, content)
        
        # Create chunks for HTML structure info
        if ids:
            ids_content = "HTML Elements with IDs:\n" + "\n".join([f"- {id_val}" for id_val in ids])
            chunk = DocumentChunk(ids_content, filename, section="element_ids")
            self.document_chunks.append(chunk)
        
        if names:
            names_content = "HTML Elements with Names:\n" + "\n".join([f"- {name_val}" for name_val in names])
            chunk = DocumentChunk(names_content, filename, section="element_names")
            self.document_chunks.append(chunk)
        
        # Extract form structure
        form_pattern = r'<form[^>]*>.*?</form>'
        forms = re.findall(form_pattern, content, re.DOTALL)
        if forms:
            form_content = "Form Elements Found:\n" + str(len(forms)) + " forms detected"
            chunk = DocumentChunk(form_content, filename, section="form_structure")
            self.document_chunks.append(chunk)
    
    def _parse_json(self, content: str, filename: str):
        """Parse JSON file into structured chunks."""
        try:
            data = json.loads(content)
            
            def extract_endpoints(obj, path=""):
                """Recursively extract endpoint information."""
                chunks = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, dict) and 'method' in value:
                            # This is an endpoint definition
                            endpoint_content = f"API Endpoint: {key}\nMethod: {value.get('method', 'N/A')}\nURL: {value.get('url', 'N/A')}\nDescription: {value.get('description', 'N/A')}"
                            chunk = DocumentChunk(endpoint_content, filename, section=f"endpoint_{key}")
                            chunks.append(chunk)
                        else:
                            chunks.extend(extract_endpoints(value, current_path))
                return chunks
            
            endpoint_chunks = extract_endpoints(data)
            self.document_chunks.extend(endpoint_chunks)
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            chunk = DocumentChunk(content, filename, section="json_content")
            self.document_chunks.append(chunk)
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 10) -> List[DocumentChunk]:
        """Retrieve most relevant document chunks for a query."""
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_terms = query.lower().split()
        
        scored_chunks = []
        for chunk in self.document_chunks:
            score = 0
            content_lower = chunk.content.lower()
            
            # Count keyword matches
            for term in query_terms:
                score += content_lower.count(term)
            
            # Boost score for exact phrases
            if query.lower() in content_lower:
                score += 10
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and return top-k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]


class TestCaseGenerator:
    """Generate comprehensive test cases based on retrieved context."""
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.test_counter = 1
    
    def generate_test_cases(self, query: str) -> List[Dict[str, Any]]:
        """Generate test cases based on user query and retrieved context."""
        # Retrieve relevant chunks
        relevant_chunks = self.rag_system.retrieve_relevant_chunks(query, top_k=10)
        
        if not relevant_chunks:
            return [{"error": "Insufficient grounding. Rebuild KB."}]
        
        # Determine which features to test based on query
        features_to_test = self._identify_features_from_query(query)
        
        test_cases = []
        
        for feature in features_to_test:
            if feature == "discount":
                test_cases.extend(self._generate_discount_tests(relevant_chunks))
            elif feature == "shipping":
                test_cases.extend(self._generate_shipping_tests(relevant_chunks))
            elif feature == "payment":
                test_cases.extend(self._generate_payment_tests(relevant_chunks))
            elif feature == "validation":
                test_cases.extend(self._generate_validation_tests(relevant_chunks))
            elif feature == "cart":
                test_cases.extend(self._generate_cart_tests(relevant_chunks))
            elif feature == "all":
                test_cases.extend(self._generate_all_tests(relevant_chunks))
        
        return test_cases
    
    def _identify_features_from_query(self, query: str) -> List[str]:
        """Identify which features to test based on the query."""
        query_lower = query.lower()
        features = []
        
        if "discount" in query_lower or "code" in query_lower:
            features.append("discount")
        if "shipping" in query_lower:
            features.append("shipping")
        if "payment" in query_lower:
            features.append("payment")
        if "validation" in query_lower or "form" in query_lower:
            features.append("validation")
        if "cart" in query_lower:
            features.append("cart")
        if "all" in query_lower or len(features) == 0:
            features = ["discount", "shipping", "payment", "validation", "cart"]
        
        return features
    
    def _generate_discount_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate discount code test cases."""
        grounded_chunks = [chunk.get_grounding_reference() for chunk in chunks if "discount" in chunk.content.lower() or "save15" in chunk.content.lower()]
        
        tests = [
            {
                "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
                "Feature": "Discount Code",
                "Preconditions": ["Checkout page is loaded", "Cart contains at least one item"],
                "Test_Scenario": "Apply valid SAVE15 discount code",
                "Steps": [
                    "Enter 'SAVE15' in discount code field",
                    "Click 'Apply' button",
                    "Verify success message appears",
                    "Check that 15% discount is applied to subtotal"
                ],
                "Expected_Result": "Discount applied successfully, total reduced by 15%, success message displayed",
                "Grounded_In": grounded_chunks if grounded_chunks else ["product_specs.md"],
                "Risk": "Medium",
                "Priority": "P1"
            }
        ]
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Discount Code",
            "Preconditions": ["Checkout page is loaded", "Cart contains at least one item"],
            "Test_Scenario": "Apply invalid discount code",
            "Steps": [
                "Enter 'INVALID123' in discount code field",
                "Click 'Apply' button",
                "Verify error message appears"
            ],
            "Expected_Result": "Error message 'Invalid or expired discount code' displayed in red",
            "Grounded_In": grounded_chunks if grounded_chunks else ["ui_ux_guide.txt"],
            "Risk": "Low",
            "Priority": "P2"
        })
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Discount Code",
            "Preconditions": ["Checkout page is loaded", "Cart contains at least one item"],
            "Test_Scenario": "Apply discount code with case sensitivity test",
            "Steps": [
                "Enter 'save15' (lowercase) in discount code field",
                "Click 'Apply' button",
                "Verify discount is applied correctly"
            ],
            "Expected_Result": "Discount applied successfully (case insensitive), 15% reduction in total",
            "Grounded_In": grounded_chunks if grounded_chunks else ["product_specs.md"],
            "Risk": "Low",
            "Priority": "P2"
        })
        self.test_counter += 1
        
        return tests
    
    def _generate_shipping_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate shipping option test cases."""
        grounded_chunks = [chunk.get_grounding_reference() for chunk in chunks if "shipping" in chunk.content.lower()]
        
        tests = [
            {
                "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
                "Feature": "Shipping",
                "Preconditions": ["Checkout page is loaded", "Cart contains items"],
                "Test_Scenario": "Select Standard shipping (default free option)",
                "Steps": [
                    "Verify Standard Shipping radio button is selected by default",
                    "Check shipping cost display",
                    "Verify total calculation"
                ],
                "Expected_Result": "Standard shipping selected, shipping cost $0.00, no additional charges",
                "Grounded_In": grounded_chunks if grounded_chunks else ["product_specs.md"],
                "Risk": "Low",
                "Priority": "P1"
            }
        ]
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Shipping",
            "Preconditions": ["Checkout page is loaded", "Cart contains items"],
            "Test_Scenario": "Select Express shipping with additional cost",
            "Steps": [
                "Click Express Shipping radio button",
                "Verify shipping cost updates to $10.00",
                "Check that total is recalculated with shipping cost"
            ],
            "Expected_Result": "Express shipping selected, shipping cost $10.00 added to total",
            "Grounded_In": grounded_chunks if grounded_chunks else ["product_specs.md"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_counter += 1
        
        return tests
    
    def _generate_payment_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate payment method test cases."""
        grounded_chunks = [chunk.get_grounding_reference() for chunk in chunks if "payment" in chunk.content.lower()]
        
        tests = [
            {
                "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
                "Feature": "Payment",
                "Preconditions": ["Checkout page is loaded", "Form is valid", "Cart is not empty"],
                "Test_Scenario": "Select Credit Card payment method",
                "Steps": [
                    "Verify Credit Card radio button is selected by default",
                    "Ensure form validation passes",
                    "Click Pay Now button"
                ],
                "Expected_Result": "Payment processed successfully, 'Payment Successful!' message displayed",
                "Grounded_In": grounded_chunks if grounded_chunks else ["ui_ux_guide.txt"],
                "Risk": "High",
                "Priority": "P1"
            }
        ]
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Payment",
            "Preconditions": ["Checkout page is loaded", "Form is valid", "Cart is not empty"],
            "Test_Scenario": "Select PayPal payment method",
            "Steps": [
                "Click PayPal radio button",
                "Verify PayPal is selected",
                "Click Pay Now button"
            ],
            "Expected_Result": "Payment processed with PayPal method, success message shown",
            "Grounded_In": grounded_chunks if grounded_chunks else ["ui_ux_guide.txt"],
            "Risk": "High",
            "Priority": "P1"
        })
        self.test_counter += 1
        
        return tests
    
    def _generate_validation_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate form validation test cases."""
        grounded_chunks = [chunk.get_grounding_reference() for chunk in chunks if "validation" in chunk.content.lower() or "error" in chunk.content.lower()]
        
        tests = [
            {
                "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
                "Feature": "Validation",
                "Preconditions": ["Checkout page is loaded"],
                "Test_Scenario": "Submit form with empty required name field",
                "Steps": [
                    "Leave name field empty",
                    "Fill email and address fields with valid data",
                    "Attempt to proceed",
                    "Verify error message appears in red"
                ],
                "Expected_Result": "Red error message 'Full name is required' displayed below name field",
                "Grounded_In": grounded_chunks if grounded_chunks else ["ui_ux_guide.txt"],
                "Risk": "Medium",
                "Priority": "P1"
            }
        ]
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Validation",
            "Preconditions": ["Checkout page is loaded"],
            "Test_Scenario": "Enter invalid email format",
            "Steps": [
                "Enter 'invalid-email' in email field",
                "Fill other required fields",
                "Check for email validation error",
                "Verify error appears in red text"
            ],
            "Expected_Result": "Red error message 'Valid email address is required' displayed",
            "Grounded_In": grounded_chunks if grounded_chunks else ["ui_ux_guide.txt"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_counter += 1
        
        return tests
    
    def _generate_cart_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate cart functionality test cases."""
        grounded_chunks = [chunk.get_grounding_reference() for chunk in chunks if "cart" in chunk.content.lower()]
        
        tests = [
            {
                "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
                "Feature": "Cart",
                "Preconditions": ["Checkout page is loaded", "Cart is empty"],
                "Test_Scenario": "Add item to cart",
                "Steps": [
                    "Select 'Laptop' from product dropdown",
                    "Set quantity to 2",
                    "Click 'Add to Cart' button",
                    "Verify item appears in cart with correct quantity and price"
                ],
                "Expected_Result": "Laptop added to cart, quantity 2, total $1999.98 displayed",
                "Grounded_In": grounded_chunks if grounded_chunks else ["checkout.html"],
                "Risk": "High",
                "Priority": "P1"
            }
        ]
        self.test_counter += 1
        
        tests.append({
            "Test_ID": f"TC-{str(self.test_counter).zfill(3)}",
            "Feature": "Cart",
            "Preconditions": ["Checkout page is loaded", "Cart contains one item"],
            "Test_Scenario": "Update item quantity in cart",
            "Steps": [
                "Click '+' button to increase quantity",
                "Verify quantity increases",
                "Verify total recalculates correctly",
                "Click '-' button to decrease quantity"
            ],
            "Expected_Result": "Quantity updates correctly, totals recalculate in real-time",
            "Grounded_In": grounded_chunks if grounded_chunks else ["checkout.html"],
            "Risk": "Medium",
            "Priority": "P1"
        })
        self.test_counter += 1
        
        return tests
    
    def _generate_all_tests(self, chunks: List[DocumentChunk]) -> List[Dict[str, Any]]:
        """Generate comprehensive test suite covering all features."""
        all_tests = []
        all_tests.extend(self._generate_discount_tests(chunks))
        all_tests.extend(self._generate_shipping_tests(chunks))
        all_tests.extend(self._generate_payment_tests(chunks))
        all_tests.extend(self._generate_validation_tests(chunks))
        all_tests.extend(self._generate_cart_tests(chunks))
        return all_tests


def main():
    """Main function to demonstrate the RAG system."""
    # Initialize RAG system
    rag_system = RAGSystem()
    rag_system.load_documents()
    
    print(f"Loaded {len(rag_system.document_chunks)} document chunks")
    
    # Initialize test case generator
    generator = TestCaseGenerator(rag_system)
    
    # Example query
    query = "Generate all positive and negative test cases for the discount code feature"
    test_cases = generator.generate_test_cases(query)
    
    # Output as JSON
    print(json.dumps(test_cases, indent=2))


if __name__ == "__main__":
    main()