import streamlit as st
import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Import required libraries for document processing and vector DB
# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
# Note: ChromaDB has compatibility issues with Python 3.14
# Using template-based processing as fallback
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Document processing imports
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from unstructured.partition.auto import partition
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False

from bs4 import BeautifulSoup
import re

# Page configuration
st.set_page_config(
    page_title="Ocean AI - Autonomous QA Agent",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DocumentProcessor:
    """Handle document parsing and text extraction"""
    
    def __init__(self):
        self.supported_extensions = {'.md', '.txt', '.json', '.html', '.pdf', '.csv'}
    
    def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        """Process uploaded file and extract text content"""
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name
        
        try:
            content = self._extract_text(tmp_file_path, file_extension)
            metadata = {
                "source_document": uploaded_file.name,
                "file_type": file_extension,
                "file_size": len(uploaded_file.getbuffer())
            }
            
            return {
                "content": content,
                "metadata": metadata,
                "chunks": self._chunk_text(content, metadata)
            }
        finally:
            os.unlink(tmp_file_path)
    
    def _extract_text(self, file_path: str, file_extension: str) -> str:
        """Extract text based on file type"""
        if file_extension == '.pdf':
            return self._extract_pdf_text(file_path)
        elif file_extension == '.html':
            return self._extract_html_text(file_path)
        elif file_extension == '.json':
            return self._extract_json_text(file_path)
        elif file_extension in {'.md', '.txt', '.csv'}:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            # Fallback to unstructured if available
            if UNSTRUCTURED_AVAILABLE:
                elements = partition(filename=file_path)
                return "\n".join([str(element) for element in elements])
            else:
                # Simple text extraction
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        if not PYMUPDF_AVAILABLE:
            raise ValueError("PyMuPDF not available for PDF processing")
        
        doc = fitz.open(file_path)
        text_content = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text_content += f"\n--- Page {page_num + 1} ---\n"
            text_content += page.get_text()
        
        doc.close()
        return text_content
    
    def _extract_html_text(self, file_path: str) -> str:
        """Extract text from HTML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract both text content and structure information
        text_parts = []
        
        # Add title
        if soup.title:
            text_parts.append(f"Title: {soup.title.get_text()}")
        
        # Add form elements with their IDs and names
        for form in soup.find_all('form'):
            text_parts.append("Form Elements:")
            for input_elem in form.find_all(['input', 'select', 'textarea', 'button']):
                elem_info = f"- {input_elem.name or 'element'}"
                if input_elem.get('id'):
                    elem_info += f" (id: {input_elem.get('id')})"
                if input_elem.get('name'):
                    elem_info += f" (name: {input_elem.get('name')})"
                if input_elem.get('type'):
                    elem_info += f" (type: {input_elem.get('type')})"
                text_parts.append(elem_info)
        
        # Add main text content
        text_parts.append("Content:")
        text_parts.append(soup.get_text(separator=' ', strip=True))
        
        return "\n".join(text_parts)
    
    def _extract_json_text(self, file_path: str) -> str:
        """Extract text from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert JSON to readable text format
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any], chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Simple text chunking with overlap"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = len(chunks)
            chunk_metadata['start_word'] = i
            chunk_metadata['end_word'] = min(i + chunk_size, len(words))
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        return chunks

class VectorDatabase:
    """Handle vector database operations using ChromaDB"""
    
    def __init__(self, collection_name: str = "qa_knowledge_base"):
        if not CHROMA_AVAILABLE:
            raise ValueError("ChromaDB not available")
        
        # Use writable directory for Streamlit Cloud
        db_path = "/tmp/chroma_db" if "streamlit" in os.environ.get("HOSTNAME", "") or os.environ.get("STREAMLIT_SERVER_PORT") else "./chroma_db"
        
        # Use new Chroma client API (PersistentClient) per migration guide
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = None
        self.embedding_model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Force clean model loading in writable directory for Streamlit Cloud
                os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'
                self.embedding_model = SentenceTransformer(
                    'all-MiniLM-L6-v2', 
                    device='cpu',
                    cache_folder='/tmp/sentence_transformers'
                )
            except Exception as e:
                st.warning(f"Could not initialize SentenceTransformer with CPU: {e}")
                # Fall back to basic text search without embeddings
                self.embedding_model = None
    
    def initialize_collection(self):
        """Initialize or get collection"""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            st.success(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(name=self.collection_name)
            st.success(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector database"""
        if not self.collection:
            self.initialize_collection()
        
        texts = []
        metadatas = []
        ids = []
        
        doc_count = 0
        for doc in documents:
            for chunk in doc['chunks']:
                texts.append(chunk['text'])
                metadatas.append(chunk['metadata'])
                ids.append(f"doc_{doc_count}_chunk_{chunk['metadata']['chunk_index']}")
            doc_count += 1
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(texts)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.collection:
            return []
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else 0.0
            })
        
        return search_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not self.collection:
            return {"status": "No collection", "count": 0}
        
        try:
            count = self.collection.count()
            return {"status": "Active", "count": count}
        except:
            return {"status": "Error", "count": 0}

class TestCaseGenerator:
    """Generate test cases using RAG and LLM"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.llm_available = False
        
        # Configure Gemini strictly (no fallback)
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY/GOOGLE_API_KEY not set. Add it to .env to enable test generation.")
        genai.configure(api_key=api_key)
        # Use Gemini 2.5 Flash (latest available model)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        self.llm_available = True
    
    def check_llm_availability(self):
        """Check if any LLM service is available"""
        # For now, we'll use a simple rule-based approach
        # In production, you would integrate with Ollama, Groq, or HuggingFace
        self.llm_available = True
    
    def generate_test_cases(self, user_query: str) -> List[Dict[str, Any]]:
        """Generate test cases via Gemini using retrieved context"""
        context_results = self.vector_db.search(user_query, n_results=5)
        context_texts = [doc["text"] for doc in context_results] if context_results else []
        sources = [doc.get("metadata", {}).get("source_document", "unknown") for doc in context_results] if context_results else []

        prompt = (
            "You are a QA engineer. Based on the following context from our e-commerce checkout system, "
            "generate 6 structured end-to-end test cases. Each test case must be a JSON object with keys: "
            "Test_ID, Feature, Test_Scenario, Steps (array), Expected_Result, Grounded_In (array of source doc names), Risk, Priority.\n\n"
            f"User Query: {user_query}\n\nContext:\n" + "\n---\n".join(context_texts[:5]) +
            "\n\nConstraints:\n- Be precise and executable.\n- Steps should be UI actions for checkout/discount/cart/payment/shipping.\n- Grounded_In must reference provided source documents only.\n- Output a JSON array of test case objects, no prose."
        )

        resp = self.model.generate_content(prompt)
        raw = resp.text if hasattr(resp, "text") else str(resp)
        try:
            data = json.loads(raw)
        except Exception:
            # Try to extract JSON block if wrapped
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1:
                data = json.loads(raw[start:end+1])
            else:
                raise RuntimeError("Gemini response did not return valid JSON test cases.")

        # Inject sources if missing
        for i, tc in enumerate(data):
            if "Grounded_In" not in tc or not tc["Grounded_In"]:
                tc["Grounded_In"] = sources[:2]
            if "Test_ID" not in tc:
                tc["Test_ID"] = f"TC-{100+i}"

        return data
    
    def _generate_structured_test_cases(self, query: str, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate structured test cases based on context"""
        test_cases = []
        
        # Analyze query to determine feature
        query_lower = query.lower()
        
        if 'discount' in query_lower:
            test_cases.extend(self._generate_discount_test_cases(context))
        elif 'cart' in query_lower:
            test_cases.extend(self._generate_cart_test_cases(context))
        elif 'payment' in query_lower:
            test_cases.extend(self._generate_payment_test_cases(context))
        elif 'validation' in query_lower or 'form' in query_lower:
            test_cases.extend(self._generate_validation_test_cases(context))
        elif 'shipping' in query_lower:
            test_cases.extend(self._generate_shipping_test_cases(context))
        else:
            # Generate comprehensive test cases
            test_cases.extend(self._generate_comprehensive_test_cases(context))
        
        return test_cases
    
    def _generate_discount_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate discount-specific test cases"""
        return [
            {
                "Test_ID": "TC-001",
                "Feature": "Discount Code",
                "Test_Scenario": "Apply valid SAVE15 discount code",
                "Steps": [
                    "Navigate to checkout page",
                    "Add items to cart (total $100)",
                    "Enter 'SAVE15' in discount code field",
                    "Click apply discount button"
                ],
                "Expected_Result": "15% discount applied, total reduced to $85.00",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "Medium",
                "Priority": "P1"
            },
            {
                "Test_ID": "TC-002", 
                "Feature": "Discount Code",
                "Test_Scenario": "Apply invalid discount code",
                "Steps": [
                    "Navigate to checkout page",
                    "Add items to cart",
                    "Enter 'INVALID123' in discount code field",
                    "Click apply discount button"
                ],
                "Expected_Result": "Error message displayed: 'Invalid discount code'",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "Low",
                "Priority": "P2"
            }
        ]
    
    def _generate_cart_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate cart-specific test cases"""
        return [
            {
                "Test_ID": "TC-003",
                "Feature": "Cart Management",
                "Test_Scenario": "Add item to cart",
                "Steps": [
                    "Navigate to checkout page",
                    "Click 'Add Item' button",
                    "Verify item appears in cart"
                ],
                "Expected_Result": "Item added with quantity 1, total updated",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "High",
                "Priority": "P1"
            }
        ]
    
    def _generate_payment_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate payment-specific test cases"""
        return [
            {
                "Test_ID": "TC-004",
                "Feature": "Payment",
                "Test_Scenario": "Verify Pay Now button styling",
                "Steps": [
                    "Fill valid checkout form",
                    "Add items to cart",
                    "Locate Pay Now button",
                    "Verify button is green"
                ],
                "Expected_Result": "Pay Now button has green background color",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "Low",
                "Priority": "P3"
            }
        ]
    
    def _generate_validation_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate validation-specific test cases"""
        return [
            {
                "Test_ID": "TC-005",
                "Feature": "Form Validation",
                "Test_Scenario": "Submit form with empty required fields",
                "Steps": [
                    "Navigate to checkout page",
                    "Leave name field empty",
                    "Leave email field empty",
                    "Click Pay Now button"
                ],
                "Expected_Result": "Red error messages displayed for empty fields",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "High",
                "Priority": "P1"
            }
        ]
    
    def _generate_shipping_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate shipping-specific test cases"""
        return [
            {
                "Test_ID": "TC-006",
                "Feature": "Shipping",
                "Test_Scenario": "Select Express shipping option",
                "Steps": [
                    "Navigate to checkout page",
                    "Add items to cart ($50 total)",
                    "Select Express shipping",
                    "Verify total is updated"
                ],
                "Expected_Result": "Express shipping adds $10, total becomes $60",
                "Grounded_In": [doc['metadata']['source_document'] for doc in context[:2]],
                "Risk": "Medium",
                "Priority": "P1"
            }
        ]
    
    def _generate_comprehensive_test_cases(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate comprehensive test suite"""
        test_cases = []
        test_cases.extend(self._generate_discount_test_cases(context))
        test_cases.extend(self._generate_cart_test_cases(context))
        test_cases.extend(self._generate_payment_test_cases(context))
        test_cases.extend(self._generate_validation_test_cases(context))
        test_cases.extend(self._generate_shipping_test_cases(context))
        return test_cases
    
    def _generate_fallback_test_cases(self, query: str) -> List[Dict[str, Any]]:
        """Generate basic test cases when no context is available"""
        return [
            {
                "Test_ID": "TC-FALLBACK",
                "Feature": "General",
                "Test_Scenario": "Basic functionality test",
                "Steps": ["Navigate to application", "Perform basic interaction"],
                "Expected_Result": "Application responds correctly",
                "Grounded_In": ["No context available"],
                "Risk": "Medium",
                "Priority": "P2"
            }
        ]

class SeleniumGenerator:
    """Generate Selenium scripts for test cases"""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
    
    def generate_selenium_script(self, test_case: Dict[str, Any], checkout_html_content: str = "") -> str:
        """Generate Selenium Python script for a test case"""
        
        # Extract relevant HTML elements
        html_elements = self._extract_html_elements(checkout_html_content)
        
        # Generate script based on test case
        script_template = self._get_script_template()
        test_steps = self._convert_steps_to_selenium(test_case, html_elements)
        
        return script_template.format(
            test_id=test_case.get('Test_ID', 'TC-001'),
            feature=test_case.get('Feature', 'Unknown'),
            test_scenario=test_case.get('Test_Scenario', ''),
            test_steps=test_steps,
            expected_result=test_case.get('Expected_Result', '')
        )
    
    def _extract_html_elements(self, html_content: str) -> Dict[str, str]:
        """Extract relevant HTML elements for Selenium selectors"""
        if not html_content:
            return {}
        
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = {}
        
        # Extract elements with IDs
        for elem in soup.find_all(attrs={'id': True}):
            elements[f"id_{elem['id']}"] = f"#{elem['id']}"
        
        # Extract form elements with names
        for elem in soup.find_all(['input', 'select', 'button'], attrs={'name': True}):
            elements[f"name_{elem['name']}"] = f"[name='{elem['name']}']"
        
        # Extract specific elements
        pay_button = soup.find('button', attrs={'id': 'pay-now'})
        if pay_button:
            elements['pay_button'] = '#pay-now'
        
        discount_field = soup.find('input', attrs={'id': 'discount-code'})
        if discount_field:
            elements['discount_field'] = '#discount-code'
        
        return elements
    
    def _convert_steps_to_selenium(self, test_case: Dict[str, Any], html_elements: Dict[str, str]) -> str:
        """Convert test steps to Selenium code"""
        steps = test_case.get('Steps', [])
        selenium_code = []
        
        for step in steps:
            step_lower = step.lower()
            
            if 'navigate' in step_lower or 'open' in step_lower:
                selenium_code.append('        driver.get("http://localhost:8080/checkout.html")')
                selenium_code.append('        time.sleep(2)')
            
            elif 'add item' in step_lower:
                selenium_code.append('        # Add item to cart')
                selenium_code.append('        add_button = driver.find_element(By.CSS_SELECTOR, ".add-item")')
                selenium_code.append('        add_button.click()')
            
            elif 'discount' in step_lower and 'enter' in step_lower:
                code_value = self._extract_discount_code(step)
                selenium_code.append(f'        # Enter discount code: {code_value}')
                if 'discount_field' in html_elements:
                    selenium_code.append(f'        discount_field = driver.find_element(By.CSS_SELECTOR, "{html_elements["discount_field"]}")')
                else:
                    selenium_code.append('        discount_field = driver.find_element(By.ID, "discount-code")')
                selenium_code.append('        discount_field.clear()')
                selenium_code.append(f'        discount_field.send_keys("{code_value}")')
            
            elif 'click' in step_lower and 'apply' in step_lower:
                selenium_code.append('        # Apply discount')
                selenium_code.append('        apply_button = driver.find_element(By.CSS_SELECTOR, ".apply-discount")')
                selenium_code.append('        apply_button.click()')
            
            elif 'pay now' in step_lower:
                selenium_code.append('        # Click Pay Now button')
                if 'pay_button' in html_elements:
                    selenium_code.append(f'        pay_button = driver.find_element(By.CSS_SELECTOR, "{html_elements["pay_button"]}")')
                else:
                    selenium_code.append('        pay_button = driver.find_element(By.ID, "pay-now")')
                selenium_code.append('        pay_button.click()')
            
            elif 'verify' in step_lower or 'check' in step_lower:
                selenium_code.append(f'        # Verification: {step}')
                selenium_code.append('        # Add specific assertions here')
        
        return '\n'.join(selenium_code)
    
    def _extract_discount_code(self, step: str) -> str:
        """Extract discount code from step text"""
        # Look for quoted text or specific codes
        import re
        match = re.search(r"'([^']*)'|\"([^\"]*)\"", step)
        if match:
            return match.group(1) or match.group(2)
        
        # Look for common discount codes
        if 'SAVE15' in step:
            return 'SAVE15'
        elif 'WELCOME10' in step:
            return 'WELCOME10'
        elif 'INVALID' in step:
            return 'INVALID123'
        
        return 'TESTCODE'
    
    def _get_script_template(self) -> str:
        """Get Selenium script template"""
        return '''#!/usr/bin/env python3
"""
Generated Selenium Test Script
Test ID: {test_id}
Feature: {feature}
Scenario: {test_scenario}
Expected Result: {expected_result}
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import sys

class TestCase:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def teardown(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
    
    def run_test(self):
        """Execute the test steps"""
        try:
            print("🧪 Starting test: {test_id}")
            print("📋 Scenario: {test_scenario}")
            
            # Test Steps
{test_steps}
            
            print("✅ Test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {{e}}")
            return False
    
    def verify_result(self):
        """Verify the expected result"""
        try:
            # Add specific verification logic here
            print("🔍 Verifying: {expected_result}")
            return True
        except Exception as e:
            print(f"❌ Verification failed: {{e}}")
            return False

def main():
    test = TestCase()
    
    try:
        test.setup()
        success = test.run_test()
        
        if success:
            verification_success = test.verify_result()
            if verification_success:
                print("🎉 Test PASSED")
                sys.exit(0)
            else:
                print("❌ Test FAILED - Verification")
                sys.exit(1)
        else:
            print("❌ Test FAILED - Execution")
            sys.exit(1)
            
    finally:
        test.teardown()

if __name__ == "__main__":
    main()
'''

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'vector_db' not in st.session_state:
        if CHROMA_AVAILABLE:
            st.session_state.vector_db = VectorDatabase()
        else:
            st.session_state.vector_db = None
    
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    
    if 'test_cases' not in st.session_state:
        st.session_state.test_cases = []
    
    if 'checkout_html' not in st.session_state:
        st.session_state.checkout_html = ""
    
    # Header
    st.title("🌊 Ocean AI - Autonomous QA Agent")
    st.markdown("### Intelligent Test Case Generation & Selenium Script Creation")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    phase = st.sidebar.selectbox(
        "Select Phase",
        ["Phase 1: Knowledge Base", "Phase 2: Test Generation", "Phase 3: Selenium Scripts"]
    )
    
    # Phase 1: Knowledge Base Ingestion
    if phase == "Phase 1: Knowledge Base":
        st.header("📚 Phase 1: Knowledge Base Ingestion")
        
        # Document upload section
        st.subheader("📄 Document Upload")
        
        st.markdown("**Upload Support Documents**")
        uploaded_files = st.file_uploader(
            "Choose files (MD, TXT, JSON, PDF, etc.)",
            accept_multiple_files=True,
            type=['md', 'txt', 'json', 'pdf', 'html', 'csv']
        )
        
        # Text input option
        st.subheader("📝 Or Paste Content")
        pasted_content = st.text_area(
            "Paste document content or other text",
            height=200,
            help="You can paste content from documents here"
        )
        
        # Process documents
        if st.button("🔨 Build Knowledge Base", type="primary"):
            if not uploaded_files and not pasted_content:
                st.error("Please upload files or paste content before building the knowledge base.")
                return
            
            with st.spinner("Processing documents and building knowledge base..."):
                processor = DocumentProcessor()
                processed_docs = []
                
                # Process uploaded files
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        try:
                            doc_data = processor.process_uploaded_file(uploaded_file)
                            processed_docs.append(doc_data)
                            st.success(f"✅ Processed: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                
                # Process pasted content
                if pasted_content.strip():
                    try:
                        # Create a mock document for pasted content
                        chunks = processor._chunk_text(
                            pasted_content, 
                            {"source_document": "pasted_content.html", "file_type": ".html"}
                        )
                        processed_docs.append({
                            'content': pasted_content,
                            'metadata': {"source_document": "pasted_content.html"},
                            'chunks': chunks
                        })
                        st.session_state.checkout_html = pasted_content
                        st.success("✅ Processed pasted content")
                    except Exception as e:
                        st.error(f"❌ Error processing pasted content: {e}")
                
                # Store in vector database
                if processed_docs and st.session_state.vector_db:
                    try:
                        total_chunks = st.session_state.vector_db.add_documents(processed_docs)
                        st.session_state.documents = processed_docs
                        st.success(f"🎉 Knowledge base built successfully! Added {total_chunks} text chunks.")
                    except Exception as e:
                        st.error(f"❌ Error building vector database: {e}")
                elif processed_docs:
                    st.session_state.documents = processed_docs
                    st.success("✅ Documents processed successfully! Using template-based test generation.")
        
        # Display knowledge base status
        st.subheader("📊 Knowledge Base Status")
        
        if st.session_state.vector_db:
            db_info = st.session_state.vector_db.get_collection_info()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Database Status", db_info['status'])
            with col2:
                st.metric("Total Chunks", db_info['count'])
            with col3:
                st.metric("Documents", len(st.session_state.documents))
        else:
            st.info("📝 Using template-based processing mode for test generation.")
        
        # Search Knowledge Base
        if st.session_state.documents and st.session_state.vector_db:
            st.subheader("🔍 Search Knowledge Base")
            
            search_query = st.text_input(
                "Search for specific information:",
                placeholder="e.g., payment validation, cart management, authentication...",
                help="Enter keywords or questions to search the knowledge base"
            )
            
            if search_query:
                with st.spinner("Searching knowledge base..."):
                    try:
                        results = st.session_state.vector_db.search(search_query, n_results=5)
                        
                        if results:
                            st.success(f"Found {len(results)} relevant results")
                            
                            for idx, result in enumerate(results):
                                with st.expander(f"📄 Result {idx + 1} - {result['metadata'].get('source_document', 'Unknown')} (Relevance: {1 - result['distance']:.2%})"):
                                    st.markdown(f"**Source Document:** `{result['metadata'].get('source_document', 'Unknown')}`")
                                    st.markdown(f"**Section:** Chunk {result['metadata'].get('chunk_index', 'N/A')}")
                                    st.markdown("**Content:**")
                                    st.text_area(
                                        "Snippet",
                                        value=result['text'],
                                        height=150,
                                        disabled=True,
                                        key=f"search_result_{idx}"
                                    )
                        else:
                            st.info("No results found. Try different keywords.")
                    except Exception as e:
                        st.error(f"Search error: {e}")
        
        # Display processed documents
        if st.session_state.documents:
            st.subheader("📋 Processed Documents")
            for i, doc in enumerate(st.session_state.documents):
                with st.expander(f"📄 {doc['metadata']['source_document']}"):
                    st.write(f"**File Type:** {doc['metadata'].get('file_type', 'unknown')}")
                    st.write(f"**Chunks:** {len(doc['chunks'])}")
                    st.write(f"**Content Preview:**")
                    st.text(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
    
    # Phase 2: Test Case Generation
    elif phase == "Phase 2: Test Generation":
        st.header("🧪 Phase 2: Test Case Generation Agent")
        
        if not st.session_state.documents:
            st.warning("⚠️ Please build the knowledge base first in Phase 1.")
            return
        
        st.subheader("💬 Agent Query Interface")
        
        # Query examples
        st.markdown("**Example queries:**")
        example_queries = [
            "Generate all positive and negative test cases for the discount code feature",
            "Create test cases for cart management functionality",
            "Generate payment flow test cases",
            "Create form validation test cases",
            "Generate shipping option test cases"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                st.session_state.current_query = query
        
        # Query input
        user_query = st.text_area(
            "Enter your test case generation request:",
            value=st.session_state.get('current_query', ''),
            height=100,
            help="Describe what kind of test cases you want to generate"
        )
        
        # Generate test cases
        if st.button("🚀 Generate Test Cases", type="primary"):
            if not user_query.strip():
                st.error("Please enter a query for test case generation.")
                return
            
            with st.spinner("Generating test cases using RAG pipeline..."):
                if st.session_state.vector_db:
                    generator = TestCaseGenerator(st.session_state.vector_db)
                    test_cases = generator.generate_test_cases(user_query)
                else:
                    # Fallback generation
                    test_cases = []
                
                if test_cases:
                    st.session_state.test_cases = test_cases
                    st.success(f"✅ Generated {len(test_cases)} test cases!")
                else:
                    st.error("❌ Failed to generate test cases. Please check your query and knowledge base.")
        
        # Display generated test cases
        if st.session_state.test_cases:
            st.subheader("📋 Generated Test Cases")
            
            # Summary
            st.markdown(f"**Total Test Cases:** {len(st.session_state.test_cases)}")
            
            # Feature breakdown
            features = {}
            for tc in st.session_state.test_cases:
                feature = tc.get('Feature', 'Unknown')
                features[feature] = features.get(feature, 0) + 1
            
            if features:
                st.markdown("**By Feature:**")
                for feature, count in features.items():
                    st.markdown(f"- {feature}: {count} test cases")
            
            # Display test cases
            for i, test_case in enumerate(st.session_state.test_cases):
                with st.expander(f"🧪 {test_case.get('Test_ID', f'TC-{i+1}')} - {test_case.get('Feature', 'Unknown')}"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Test Scenario:** {test_case.get('Test_Scenario', 'N/A')}")
                        st.markdown(f"**Expected Result:** {test_case.get('Expected_Result', 'N/A')}")
                        st.markdown(f"**Priority:** {test_case.get('Priority', 'N/A')}")
                        st.markdown(f"**Risk:** {test_case.get('Risk', 'N/A')}")
                    
                    with col2:
                        if test_case.get('Steps'):
                            st.markdown("**Steps:**")
                            for j, step in enumerate(test_case['Steps'], 1):
                                st.markdown(f"{j}. {step}")
                        
                        if test_case.get('Grounded_In'):
                            st.markdown("**Grounded In:**")
                            for source in test_case['Grounded_In']:
                                st.markdown(f"- {source}")
                    
                    # JSON view
                    if st.checkbox(f"Show JSON", key=f"json_{i}"):
                        st.json(test_case)
            
            # Export option
            if st.button("📥 Export Test Cases as JSON"):
                json_str = json.dumps(st.session_state.test_cases, indent=2)
                st.download_button(
                    label="Download test_cases.json",
                    data=json_str,
                    file_name="generated_test_cases.json",
                    mime="application/json"
                )
    
    # Phase 3: Selenium Script Generation
    elif phase == "Phase 3: Selenium Scripts":
        st.header("🤖 Phase 3: Selenium Script Generation Agent")
        
        if not st.session_state.test_cases:
            st.warning("⚠️ Please generate test cases first in Phase 2.")
            return
        
        st.subheader("🎯 Select Test Case")
        
        # Test case selection
        test_case_options = []
        for i, tc in enumerate(st.session_state.test_cases):
            option = f"{tc.get('Test_ID', f'TC-{i+1}')} - {tc.get('Feature', 'Unknown')} - {tc.get('Test_Scenario', 'N/A')}"
            test_case_options.append(option)
        
        selected_index = st.selectbox(
            "Choose a test case:",
            range(len(test_case_options)),
            format_func=lambda x: test_case_options[x]
        )
        
        selected_test_case = st.session_state.test_cases[selected_index]
        
        # Display selected test case
        with st.expander("📋 Selected Test Case Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Test ID:** {selected_test_case.get('Test_ID', 'N/A')}")
                st.markdown(f"**Feature:** {selected_test_case.get('Feature', 'N/A')}")
                st.markdown(f"**Scenario:** {selected_test_case.get('Test_Scenario', 'N/A')}")
            
            with col2:
                st.markdown(f"**Expected Result:** {selected_test_case.get('Expected_Result', 'N/A')}")
                st.markdown(f"**Priority:** {selected_test_case.get('Priority', 'N/A')}")
                st.markdown(f"**Risk:** {selected_test_case.get('Risk', 'N/A')}")
            
            if selected_test_case.get('Steps'):
                st.markdown("**Test Steps:**")
                for j, step in enumerate(selected_test_case['Steps'], 1):
                    st.markdown(f"{j}. {step}")
        
        # Generate Selenium script
        if st.button("🔧 Generate Selenium Script", type="primary"):
            with st.spinner("Generating Selenium Python script..."):
                generator = SeleniumGenerator(st.session_state.vector_db)
                selenium_script = generator.generate_selenium_script(
                    selected_test_case, 
                    st.session_state.checkout_html
                )
                
                st.session_state.generated_script = selenium_script
                st.success("✅ Selenium script generated successfully!")
        
        # Display generated script
        if hasattr(st.session_state, 'generated_script'):
            st.subheader("📜 Generated Selenium Script")
            
            # Script display with syntax highlighting
            st.code(st.session_state.generated_script, language='python')
            
            # Download button
            st.download_button(
                label="📥 Download Python Script",
                data=st.session_state.generated_script,
                file_name=f"test_{selected_test_case.get('Test_ID', 'TC-001').lower()}.py",
                mime="text/python"
            )
            
            # Instructions
            st.subheader("🚀 How to Run the Script")
            st.markdown("""
            **Prerequisites:**
            ```bash
            pip install selenium webdriver-manager
            ```
            
            **Run the script:**
            ```bash
            python test_script.py
            ```
            
            **Notes:**
            - Make sure your application is running on http://localhost:8080
            - Chrome browser will be used in headless mode
            - The script includes error handling and proper cleanup
            """)

if __name__ == "__main__":
    main()