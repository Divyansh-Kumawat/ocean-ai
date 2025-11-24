# 🌊 Ocean AI - Autonomous QA Agent (Streamlit)

## Complete 3-Phase QA Automation System

This Streamlit application implements the full autonomous QA agent as specified in the assignment, providing:

### **Phase 1: Knowledge Base Ingestion & UI**
- ✅ Document upload (MD, TXT, JSON, PDF, HTML, CSV)
- ✅ Content parsing with multiple libraries
- ✅ Vector database ingestion (ChromaDB)
- ✅ Text chunking with metadata preservation
- ✅ Embedding generation using Sentence Transformers

### **Phase 2: Test Case Generation Agent**
- ✅ RAG pipeline with query embedding
- ✅ Context retrieval from vector database
- ✅ Structured test case generation
- ✅ JSON and Markdown table output
- ✅ Source document grounding

### **Phase 3: Selenium Script Generation Agent**
- ✅ Test case selection interface
- ✅ HTML content analysis
- ✅ Runnable Selenium Python script generation
- ✅ Appropriate selector extraction
- ✅ High-quality executable code output

---

## 🚀 Quick Start

### **Option 1: Auto Setup (Recommended)**
```bash
# Run the automated setup
python launch_streamlit.py

# This will:
# - Check Python version
# - Install dependencies
# - Launch Streamlit app
# - Open browser at http://localhost:8501
```

### **Option 2: Manual Setup**
```bash
# Install dependencies
pip install -r requirements-streamlit.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Open browser: http://localhost:8501
```

### **Option 3: Demo Mode**
```bash
# Create sample data first
python demo_setup.py

# Then launch app
python launch_streamlit.py
```

---

## 📋 Requirements

### **Core Dependencies**
```bash
streamlit>=1.28.0              # Main UI framework
chromadb>=0.4.15               # Vector database
sentence-transformers>=2.2.0   # Embeddings
beautifulsoup4>=4.12.0         # HTML parsing
pymupdf>=1.23.0                # PDF processing
unstructured>=0.10.0           # Document parsing
selenium>=4.15.0               # Script generation
```

### **System Requirements**
- **Python 3.8+**
- **Chrome browser** (for Selenium scripts)
- **4GB+ RAM** (for embeddings)
- **Internet connection** (for model downloads)

---

## 🎯 Phase-by-Phase Guide

### **Phase 1: Knowledge Base Setup**

#### **1. Document Upload**
- **Supported formats**: MD, TXT, JSON, PDF, HTML, CSV
- **Multiple files**: Upload all your documentation
- **Paste content**: Alternative to file upload
- **Automatic parsing**: Extracts text and structure

#### **2. Content Processing**
- **Text extraction**: Format-specific parsers
- **Chunking**: 1000 characters with 200 overlap
- **Metadata**: Source document tracking
- **HTML analysis**: Form elements and IDs extracted

#### **3. Vector Database**
- **Embeddings**: Generated using all-MiniLM-L6-v2
- **Storage**: ChromaDB with persistence
- **Indexing**: Semantic search capability
- **Status monitoring**: Real-time collection info

---

### **Phase 2: Test Case Generation**

#### **1. Query Interface**
- **Natural language**: Describe what you want
- **Example queries**: Pre-built common requests
- **RAG pipeline**: Context retrieval + LLM generation

#### **2. Test Case Output**
```json
{
  "Test_ID": "TC-001",
  "Feature": "Discount Code",
  "Test_Scenario": "Apply valid SAVE15 discount code",
  "Steps": ["Navigate to checkout", "Enter code", "Verify discount"],
  "Expected_Result": "15% discount applied, total reduced",
  "Grounded_In": ["product_specs.md", "checkout.html"],
  "Risk": "Medium",
  "Priority": "P1"
}
```

#### **3. Features Covered**
- **Discount codes**: Positive/negative scenarios
- **Cart management**: Add, remove, update quantities
- **Payment flow**: Methods, validation, styling
- **Form validation**: Required fields, error messages
- **Shipping options**: Standard vs Express

---

### **Phase 3: Selenium Script Generation**

#### **1. Test Case Selection**
- **Interactive list**: All generated test cases
- **Detailed view**: Steps, expected results
- **Context aware**: HTML element mapping

#### **2. Script Generation**
- **HTML analysis**: Extract IDs, names, CSS selectors
- **Step conversion**: Natural language → Selenium code
- **Best practices**: WebDriverWait, proper cleanup
- **Error handling**: Try-catch blocks, assertions

#### **3. Output Example**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def test_discount_code():
    driver = webdriver.Chrome()
    driver.get("http://localhost:8080/checkout.html")
    
    # Add items to cart
    add_button = driver.find_element(By.CSS_SELECTOR, ".add-item")
    add_button.click()
    
    # Apply discount code
    discount_field = driver.find_element(By.ID, "discount-code")
    discount_field.send_keys("SAVE15")
    
    apply_button = driver.find_element(By.CSS_SELECTOR, ".apply-discount")
    apply_button.click()
    
    # Verify result
    total = driver.find_element(By.ID, "cart-total")
    assert "85.00" in total.text
    
    driver.quit()
```

---

## 🔧 Technical Features

### **Document Processing**
- **PDF extraction**: PyMuPDF for text and structure
- **HTML parsing**: BeautifulSoup with element detection
- **JSON handling**: Structured data to readable text
- **Unstructured support**: Advanced document parsing
- **Error handling**: Graceful fallbacks

### **Vector Database (ChromaDB)**
- **Persistent storage**: Data survives app restarts
- **Semantic search**: Natural language queries
- **Metadata filtering**: Source document tracking
- **Scalable**: Handles large document collections
- **Local deployment**: No external API dependencies

### **Embedding Models**
- **Sentence Transformers**: High-quality embeddings
- **all-MiniLM-L6-v2**: Lightweight, fast model
- **Automatic download**: First-time setup
- **CPU optimized**: Works without GPU

### **Test Case Generation**
- **RAG pipeline**: Retrieval + Generation
- **Context grounding**: All outputs cite sources
- **Structured format**: JSON schema compliance
- **Feature categorization**: Organized by functionality
- **Risk assessment**: Priority and risk levels

### **Selenium Generation**
- **HTML awareness**: Uses actual page structure
- **Selector optimization**: IDs > Names > CSS
- **WebDriver best practices**: Waits, error handling
- **Cross-browser ready**: Chrome, Firefox, Safari
- **Production quality**: Full test scripts

---

## 🎮 Usage Examples

### **Example 1: Discount Code Testing**
```
Query: "Generate all positive and negative test cases for discount codes"

Generated:
- TC-001: Valid SAVE15 code application
- TC-002: Valid WELCOME10 code application  
- TC-003: Invalid code rejection
- TC-004: Case insensitive handling
- TC-005: Empty code validation
```

### **Example 2: Form Validation**
```
Query: "Create test cases for form validation"

Generated:
- TC-006: Required field validation
- TC-007: Email format validation
- TC-008: Error message styling (red)
- TC-009: Error clearing on correction
```

### **Example 3: End-to-End Testing**
```
Query: "Generate comprehensive test suite"

Generated:
- 15+ test cases covering all features
- Positive and negative scenarios
- Boundary value testing
- Integration test cases
```

---

## 📊 Monitoring & Analytics

### **Knowledge Base Metrics**
- Total documents processed
- Number of text chunks
- Vector database size
- Processing errors/warnings

### **Test Generation Stats**
- Test cases generated
- Feature coverage breakdown
- Source document utilization
- Generation time

### **Quality Indicators**
- Source grounding percentage
- Test step completeness
- Selector availability
- Script generation success

---

## 🔍 Troubleshooting

### **Common Issues**

#### **1. ChromaDB Installation**
```bash
# Error: ChromaDB not available
pip install chromadb>=0.4.15
```

#### **2. Sentence Transformers**
```bash
# Error: Model download failed
pip install sentence-transformers>=2.2.0
# Ensure internet connection for first download
```

#### **3. PDF Processing**
```bash
# Error: PyMuPDF not found
pip install pymupdf>=1.23.0
```

#### **4. Memory Issues**
```bash
# Reduce chunk size in DocumentProcessor._chunk_text()
chunk_size = 500  # Instead of 1000
```

#### **5. Streamlit Port Conflicts**
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502
```

---

## 🚀 Deployment Options

### **Local Development**
```bash
python launch_streamlit.py
```

### **Docker Deployment**
```bash
# Build image
docker build -t ocean-ai-streamlit .

# Run container
docker run -p 8501:8501 ocean-ai-streamlit
```

### **Streamlit Cloud**
```bash
# Push to GitHub
git push origin main

# Connect at share.streamlit.io
# Auto-deploy from repository
```

### **Production Server**
```bash
# Install dependencies
pip install -r requirements-streamlit.txt

# Run with Gunicorn (for production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker streamlit_app:app
```

---

## 🎯 Assignment Compliance

### **✅ Phase 1 Requirements**
- [x] Streamlit UI for document upload
- [x] Support for MD, TXT, JSON, PDF files
- [x] Upload/paste checkout.html capability
- [x] "Build Knowledge Base" functionality
- [x] Multiple parsing libraries (unstructured, pymupdf)
- [x] Text chunking with RecursiveCharacterTextSplitter
- [x] Metadata preservation
- [x] Embedding generation (Hugging Face models)
- [x] Vector DB storage (ChromaDB)

### **✅ Phase 2 Requirements**
- [x] Agent section for test case requests
- [x] Example prompt: "Generate all positive and negative test cases for discount code feature"
- [x] RAG pipeline (embed query → retrieve → LLM)
- [x] Structured test plans in JSON format
- [x] Test case output with all required fields
- [x] Source document grounding
- [x] "Grounded_In" field referencing source documents

### **✅ Phase 3 Requirements**
- [x] Test case selection interface
- [x] "Generate Selenium Script" functionality
- [x] Receive selected test case
- [x] Retrieve checkout.html content
- [x] Retrieve documentation from vector DB
- [x] LLM generates runnable Selenium Python script
- [x] Selenium expert instructions
- [x] Appropriate selectors based on HTML
- [x] High-quality, executable code
- [x] Code block display for easy copying

---

## 🏆 Advanced Features

### **Smart Document Analysis**
- **HTML element extraction**: Form fields, buttons, IDs
- **JSON structure parsing**: API endpoints, configurations
- **PDF table recognition**: Structured data extraction
- **Markdown section mapping**: Hierarchical content

### **Intelligent Test Generation**
- **Context-aware scenarios**: Based on available features
- **Risk assessment**: Automatic priority assignment
- **Edge case identification**: Boundary value detection
- **Integration scenarios**: Multi-feature interactions

### **Production-Ready Selenium**
- **Stable selectors**: Preference hierarchy (ID > Name > CSS)
- **Proper waits**: WebDriverWait instead of sleep
- **Error handling**: Try-catch with meaningful messages
- **Cross-browser support**: Chrome, Firefox, Safari options
- **Headless mode**: CI/CD friendly configuration

---

**🎉 Your autonomous QA agent is ready! Upload documents, generate tests, and create Selenium scripts with AI assistance.**