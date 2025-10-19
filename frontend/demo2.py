# app.py
import streamlit as st
import subprocess
import os
import shutil
import re

import stat # Make sure this is imported at the top of your Streamlit script

def remove_readonly_and_try_again(func, path, excinfo):
    """
    Error handler for shutil.rmtree.
    If the error is access denied (e.g., read-only file), 
    it changes the permission and then retries the removal.
    """
    # Check if the error is due to an access problem
    if func in (os.rmdir, os.remove, os.unlink):
        # Change file permissions to allow write (full permissions)
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) 
        try:
            func(path)
        except Exception:
            # If still fails, re-raise the original error
            raise
    else:
        # For other errors, re-raise
        raise

st.set_page_config(layout="wide")
st.title("🔐 Cloq Black Box Deployment Demo")
st.header("Securely Deploying Encrypted Open-Source Code")

st.markdown("""
This demo shows how Cloq transforms a publicly visible **Open Source project** into a **secure, executable black box** for Enterprise deployment.

1. **Vendor** clones the source code.
2. **Vendor** encrypts the entire repository contents.
3. **Enterprise** decrypts and runs the code in their environment **without ever seeing the source files.**
""")

if st.button("🚀 Run Black Box Deployment Workflow"):
    # Clean up keys and previous files to ensure a fresh run
    if os.path.exists("test_keys"):
        st.warning("Cleaning up previous 'test_keys' directory...")
        
        # Use the onerror handler to fix read-only issues on Windows
        try:
            shutil.rmtree("test_keys", onerror=remove_readonly_and_try_again)
            st.success("Previous 'test_keys' cleaned successfully.")
        except Exception as e:
            st.error(f"Failed to clean 'test_keys' directory: {e}. Please manually delete or restart the system.")
            # Critical failure: Stop the test execution
            st.stop()
    st.info("Running `encryption_test.py` to simulate the full Vendor -> Enterprise lifecycle...")
    
    # FIX: Dynamically construct the absolute path to the test file
    test_script_path = os.path.join(os.path.dirname(__file__), "encryption_test.py")

    # Create a copy of the current environment
    child_env = os.environ.copy()
    # Set PYTHONIOENCODING to utf-8 to ensure the child process (encryption_test.py) 
    # encodes its output correctly, resolving the UnicodeEncodeError.
    child_env['PYTHONIOENCODING'] = 'utf-8' 

    try:
        # Run the full test script
        result = subprocess.run(
            ["python", r"C:\Users\ander\OneDrive\Documents\DubHacks 25'\cloq\tst\encryption_test.py"],
            capture_output=True,
            text=True,
            check=True,
            env=child_env, 
            timeout=60, # Set a generous timeout
            encoding="utf-8"
        )
        test_output = result.stdout
        
        st.success("Test completed successfully!")

        # --- 1. PACKAGE INTEGRITY & SECURITY ---
        st.subheader("📦 Vendor Packaging and Security")
        
        original_size = re.search(r"Original size: (\d+) bytes", test_output).group(1)
        encrypted_size = re.search(r"Encrypted size: (\d+) bytes", test_output).group(1)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Original Codebase Size", f"{original_size} bytes")
        col2.metric("Encrypted Package Size", f"{encrypted_size} bytes", 
                    delta=f"+{int(encrypted_size)-int(original_size)} bytes")
        col3.metric("Encryption Used", "Hybrid (RSA-4096 + AES-256)")

        # --- 2. BLACK BOX EXECUTION ---
        st.subheader("⚫ Enterprise: Black Box Execution")
        st.markdown("The enterprise has decrypted the package and is running the program in an isolated environment. **The source code is never directly accessed.**")
        
        # Extract the program output using the unique markers
        program_output_match = re.search(
            r"--- Start Black Box Program Output ---\n(.*?)--- End Black Box Program Output ---", 
            test_output, 
            re.DOTALL
        )
        
        if program_output_match:
            program_output = program_output_match.group(1).strip()
            
            # Use columns for visual impact
            col_code, col_output = st.columns([1, 2])
            
            with col_code:
                st.info("Source Code Status")
                st.markdown("The source code files (from the public repo) are currently present on the Enterprise machine, but they are wrapped/executed without needing to expose them as part of a public build pipeline.")
                st.code(
                    "|/project_root\n|-- package.clq (Encrypted)\n|-- private.pem (Key)\n\n# Execution environment\n$ python main_executor.py --package package.clq", 
                    language='bash'
                )

            with col_output:
                st.success("Program Output (Decrypted and Executed)")
                st.code(program_output, language='text')

            st.success("🎉 Full Black Box Deployment Successful: Functionality Preserved!")
        else:
            st.error("❌ Execution Output Not Found. Check `encryption_test.py` for warnings.")


        # --- 3. FULL LOG (Optional) ---
        with st.expander("Show Full Workflow Log"):
            st.code(test_output, language='text')
            
    except subprocess.CalledProcessError as e:
        st.error("Test Failed! See full logs below.")
        st.code(f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}", language='bash')
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e)