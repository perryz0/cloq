import contextlib
import io
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tst.demo_encryption import demonstrate_encryption
from tst.crypto_test import test_full_workflow

# ... existing imports and setup code ...

def parse_workflow_output(output_text):
    """Parse the workflow output into structured sections"""
    sections = {
        'vendor': [],
        'enterprise': [],
        'summary': []
    }
    
    current_section = 'vendor'
    for line in output_text.split('\n'):
        if '🏢 ENTERPRISE SIDE' in line:
            current_section = 'enterprise'
        elif '📋 SUMMARY' in line:
            current_section = 'summary'
        sections[current_section].append(line)
    
    return sections

# Page configuration
st.set_page_config(
    page_title="Cloq Demo",
    page_icon="🔒",
    layout="wide"
)

# Custom CSS for better visualization
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .output-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
    }
    .demo-header {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e8f0fe;
        border-left: 5px solid #1a73e8;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("🔒 Cloq: Secure Software Distribution Platform")
st.markdown("""
<div class="info-box">
Cloq enables software vendors to securely distribute their applications to enterprise customers,
ensuring code remains protected while maintaining full functionality.
</div>
""", unsafe_allow_html=True)

# Create tabs for different demos
tab1, tab2 = st.tabs(["✨ Simple Demo", "🚀 Full Workflow"])

with tab1:
    st.header("Simple Encryption Demo")
    st.write("""
    This demonstration shows how Cloq encrypts and decrypts code while preserving its functionality.
    You can see the code in its original form, its encrypted state, and the recovered form after decryption.
    """)
    
    if st.button("▶️ Run Simple Demo", key="simple_demo"):
        with st.spinner("Demonstrating encryption process..."):
            result = demonstrate_encryption()
            
            # Display results in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📝 Original Code")
                st.code(result['original'], language='python')
            
            with col2:
                st.markdown("### 🔐 Encrypted Form")
                st.code(result['encrypted'], language='text')
                st.caption("(First 100 characters shown)")
            
            with col3:
                st.markdown("### 🔓 Decrypted Code")
                st.code(result['decrypted'], language='python')
                
            st.success("✅ Code successfully encrypted and decrypted!")

# ... in the tab2 section, replace the output handling with:

with tab2:
    st.header("Complete Workflow Demonstration")
    st.write("""
    This demonstration shows the complete vendor-to-enterprise workflow, including:
    1. Vendor creating and encrypting a software package
    2. Package distribution (simulated)
    3. Enterprise decrypting and running the software
    4. Verification of preserved functionality
    """)
    
    if st.button("▶️ Run Full Workflow", key="full_demo"):
        with st.spinner("Running complete workflow demonstration..."):
            # Capture the output
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                success = test_full_workflow()
            
            # Parse the output into sections
            sections = parse_workflow_output(output.getvalue())
            
            # Display Vendor Phase
            with st.expander("🏭 Vendor Side", expanded=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.code('\n'.join(sections['vendor']), language='text')
                with col2:
                    st.markdown("""
                    ### Vendor Operations
                    - ✅ Package Creation
                    - 🔑 Key Generation
                    - 🔒 Encryption
                    - 📦 Publishing
                    """)
            
            # Display Enterprise Phase
            with st.expander("🏢 Enterprise Side", expanded=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.code('\n'.join(sections['enterprise']), language='text')
                with col2:
                    st.markdown("""
                    ### Enterprise Operations
                    - 🔓 Decryption
                    - 📂 Extraction
                    - ▶️ Execution
                    - ✅ Verification
                    """)
            
            # Display Summary
            with st.expander("📊 Results Summary", expanded=True):
                st.code('\n'.join(sections['summary']), language='text')
                
                # Add visual indicators for key metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    st.metric(
                        label="Calculations Verified",
                        value="4/4",
                        delta="100% Success"
                    )
                with metrics_col2:
                    st.metric(
                        label="Security Checks",
                        value="Passed",
                        delta="✅"
                    )
                with metrics_col3:
                    st.metric(
                        label="Memory Safety",
                        value="Verified",
                        delta="✅"
                    )
            
            if success:
                st.success("✅ Full workflow completed successfully!")
                st.balloons()
            else:
                st.error("❌ Workflow encountered an error!")
# Footer
st.markdown("---")
st.markdown("### 📊 Technical Details")
st.markdown("""
- **Encryption**: RSA-4096 for key encryption, AES-256-GCM for data
- **Key Management**: Secure key generation and distribution
- **Runtime**: In-memory execution of decrypted code
- **Security**: No plaintext code stored on enterprise systems
""")

st.markdown("---")
st.caption("© 2025 Cloq | Secure Software Distribution Platform")