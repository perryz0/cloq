import streamlit as st
import os
import time
import io
import contextlib
import requests
import tempfile

# some change
# another change

# --- Page Configuration ---

st.set_page_config(

    page_title="Cloq | Secure Execution Platform",

    page_icon="🔒",

    layout="wide"

)



# --- Custom CSS for Styling ---

st.markdown("""

<style>

    /* General styling */

    .stApp {

        background-color: #f0f2f6;

    }

    /* Set default text color for the app */

    body, .stApp, .stMarkdown, .stTabs, p, div, span {

        color: #333333;

    }

    h1 {

        color: #1a1a1a !important;

        font-weight: 600;

    }

    h2, h3 {

        color: #333333 !important;

        font-weight: 500;

    }

    .stButton>button {

        border-radius: 8px;

        border: 1px solid #1a1a1a;

        background-color: #ffffff;

        color: #1a1a1a;

        font-weight: 600;

        transition: all 0.2s ease-in-out;

    }

    .stButton>button:hover {

        background-color: #e9ecef;

        color: #1a1a1a;

        border-color: #1a1a1a;

    }

    /* Tab styling */

    .stTabs [data-baseweb="tab-list"] {

        gap: 24px;

        border-bottom: 2px solid #e0e0e0;

    }

    .stTabs [data-baseweb="tab"] {

        height: 50px;

        white-space: pre-wrap;

        background-color: transparent;

        border: none;

        padding-top: 10px;

        padding-bottom: 10px;

    }

    .stTabs [aria-selected="true"] {

        background-color: transparent;

        color: #1a1a1a; /* Ensure selected tab text is dark */

        border-bottom: 2px solid #1a1a1a;

    }

    /* Style the file uploader - AGGRESSIVE OVERRIDE */

    [data-testid="stFileUploader"] section {

        background-color: #fafafa !important;

        border: 2px dashed #cccccc !important;

        border-radius: 8px;

    }

    [data-testid="stFileUploader"] section * {

        color: #333333 !important;

    }

    [data-testid="stFileUploader"] svg {

        fill: #333333 !important;

    }

    [data-testid="stFileUploader"] button {

        border-color: #cccccc !important;

        background-color: #e0e0e0 !important;

        color: #333333 !important;

    }

    /* Style text inputs and text areas - AGGRESSIVE OVERRIDE */

    [data-testid="stTextInput"] input, 

    [data-testid="stTextArea"] textarea {

        background-color: #ffffff !important;

        border: 1px solid #cccccc !important;

        border-radius: 8px !important;

        padding: 10px !important;

        color: #333333 !important;

    }

</style>

""", unsafe_allow_html=True)





# --- Simulated Cryptographic Functions ---

def generate_key():

    return os.urandom(16)



def encrypt(data, key):

    return bytes([b ^ k for b, k in zip(data, key * (len(data) // len(key) + 1))])



def decrypt(data, key):

    return bytes([b ^ k for b, k in zip(data, key * (len(data) // len(key) + 1))])





# --- Main Application Title ---

st.title("Cloq: Secure Execution Platform")





# --- Tab Definitions ---

control_plane_tab, vendor_tab, enterprise_tab = st.tabs(

    ["Control Plane", "SaaS Vendor", "Enterprise Consumer"]

)





# --- Control Plane Tab ---

with control_plane_tab:

    st.header("Control Plane Interaction")

    st.info(

        """

        This tab allows you to interact directly with the Cloq Control Plane API.

        **Note:** The control plane server must be running for these operations to succeed.

        Start it with: `python -m src.cloq_cp.main`

        """

    )



    base_url = "http://localhost:8000"



    # Section 1: Health Check

    st.subheader("1. Health Check")

    if st.button("Check Server Health"):

        with st.spinner("Pinging control plane..."):

            try:

                response = requests.get(f"{base_url}/health", timeout=5)

                if response.status_code == 200:

                    health_data = response.json()

                    st.success("Control plane is healthy!")

                    st.json(health_data)

                else:

                    st.error(f"Health check failed. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane. Is it running?")

            except Exception as e:

                st.error(f"An unexpected error occurred: {e}")



    # Section 2: Upload Artifact

    st.subheader("2. Upload Artifact")

    artifact_content = st.text_area("Enter content for a new artifact:", "This is a test artifact for the Cloq control plane.", height=100)

    if st.button("Create and Upload Artifact"):

        with st.spinner("Uploading artifact..."):

            try:

                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:

                    f.write(artifact_content)

                    temp_file_path = f.name

                

                with open(temp_file_path, 'rb') as f:

                    files = {'file': ('test_artifact.txt', f, 'text/plain')}

                    response = requests.post(f"{base_url}/upload", files=files)

                

                os.unlink(temp_file_path)



                if response.status_code == 200:

                    upload_data = response.json()

                    st.success("Artifact uploaded successfully!")

                    st.session_state.last_artifact_id = upload_data.get('artifact_id')

                    st.json(upload_data)

                else:

                    st.error(f"Upload failed. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane.")

            except Exception as e:

                st.error(f"An unexpected error occurred during upload: {e}")



    # Section 3: List Artifacts

    st.subheader("3. List Artifacts")

    if st.button("Get Artifact List"):

        with st.spinner("Fetching artifact list..."):

            try:

                response = requests.get(f"{base_url}/list")

                if response.status_code == 200:

                    st.success("Artifact list retrieved.")

                    st.json(response.json())

                else:

                    st.error(f"Failed to get list. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane.")

            except Exception as e:

                st.error(f"An unexpected error occurred: {e}")



    # Section 4: Download Artifact

    st.subheader("4. Download Artifact")

    default_id = st.session_state.get('last_artifact_id', '')

    artifact_id_to_download = st.text_input("Enter Artifact ID to download:", value=default_id)

    if st.button("Download Artifact"):

        if not artifact_id_to_download:

            st.warning("Please enter an Artifact ID.")

        else:

            with st.spinner(f"Downloading artifact {artifact_id_to_download}..."):

                try:

                    response = requests.get(f"{base_url}/download/{artifact_id_to_download}")

                    if response.status_code == 200:

                        st.success("Download successful!")

                        st.text("File Content:")

                        st.code(response.text, language="")

                    else:

                        st.error(f"Download failed. Status code: {response.status_code}")

                        st.text(response.text)

                except requests.exceptions.ConnectionError:

                    st.error("Connection Error: Could not connect to the control plane.")

                except Exception as e:

                    st.error(f"An unexpected error occurred: {e}")





# --- SaaS Vendor Tab ---

with vendor_tab:

    st.header("Vendor: Seal and Publish")

    st.write(

        """

        As the SaaS Vendor, you will seal your proprietary code into an encrypted container 

        layer and publish it to a secure registry.

        """

    )



    st.subheader("Step 1: Upload and Seal Proprietary Code")

    uploaded_file = st.file_uploader("Upload your proprietary code/data (e.g., a .py or .txt file)", key="vendor_uploader")



    if uploaded_file is not None:

        if "sealed" not in st.session_state:

            st.session_state.sealed = False



        if not st.session_state.sealed:

            if st.button("Seal and Publish"):

                with st.spinner("Sealing proprietary code..."):

                    proprietary_data = uploaded_file.getvalue()

                    st.session_state.original_data = proprietary_data



                    data_encryption_key = generate_key()

                    st.session_state.data_encryption_key = data_encryption_key



                    sealed_layer = encrypt(proprietary_data, data_encryption_key)

                    st.session_state.sealed_layer = sealed_layer



                    st.session_state.wrapped_key = data_encryption_key 

                    st.session_state.sealed = True

                st.success("Proprietary code sealed and published successfully!")



        if st.session_state.sealed:

            st.subheader("Published Artifacts")

            st.write("These artifacts are now available in the secure registry.")

            

            st.write("**Sealed Image Layer (Encrypted):**")

            st.code(st.session_state.sealed_layer.hex(), language="")



            st.write("**Wrapped Execution Key:**")

            st.code(st.session_state.wrapped_key.hex(), language="")

            

            st.info("Navigate to the **Enterprise Consumer** tab to proceed with secure execution.")

    else:

        st.info("Please upload a file to begin the sealing process.")





# --- Enterprise Consumer Tab ---

with enterprise_tab:

    st.header("Enterprise: Securely Execute Software")

    st.write(

        """

        As the Enterprise Consumer, you will attest your environment, retrieve the sealed 

        container, and execute it securely.

        """

    )



    if "sealed" not in st.session_state or not st.session_state.sealed:

        st.warning("The SaaS Vendor has not published a sealed image yet. Please go to the **SaaS Vendor** tab first.")

    else:

        st.subheader("Step 1: Remote Attestation")

        st.write("The execution environment must prove its integrity to the Compliance Service.")



        if "attested" not in st.session_state:

            st.session_state.attested = False



        if not st.session_state.attested:

            if st.button("Perform Remote Attestation"):

                with st.spinner("Performing attestation..."):

                    time.sleep(1)

                    st.session_state.attested = True

                st.success("Attestation successful! Environment is trusted.")



        if st.session_state.attested:

            st.subheader("Step 2: Retrieve and Unwrap Execution Key")

            st.write("The Compliance Service has released the wrapped key.")



            if "unwrapped" not in st.session_state:

                st.session_state.unwrapped = False



            if not st.session_state.unwrapped:

                if st.button("Unwrap Execution Key"):

                    with st.spinner("Unwrapping key with private key..."):

                        time.sleep(1)

                        st.session_state.execution_key = st.session_state.wrapped_key

                        st.session_state.unwrapped = True

                    st.success("Execution Key ($K_D$) successfully retrieved!")



            if st.session_state.unwrapped:

                st.write("**Retrieved Execution Key ($K_D$):**")

                st.code(st.session_state.execution_key.hex(), language="")



                st.subheader("Step 3: In-Memory Unseal and Run")

                st.write("The sealed layer is decrypted and loaded directly into memory.")



                if st.button("Unseal and Run"):

                    with st.spinner("Decrypting layer and executing in memory..."):

                        time.sleep(1)

                        decrypted_data = decrypt(st.session_state.sealed_layer, st.session_state.execution_key)

                        

                        st.success("Container running! Proprietary code is now executing in a secure environment.")

                        

                        st.subheader("Result: Captured Output from Executed Code")

                        

                        output_capture = io.StringIO()

                        try:

                            with contextlib.redirect_stdout(output_capture):

                                exec(decrypted_data.decode('utf-8'))

                            captured_output = output_capture.getvalue()

                            st.write("The following output was captured from the code running in memory:")

                            st.code(captured_output, language="")

                        except Exception as e:

                            st.error(f"An error occurred during execution: {e}")



                        st.balloons()

                        st.info("The decrypted code was executed in memory and **never** written to disk on the enterprise side.")

import streamlit as st
import os
import time
import io
import contextlib
import requests
import tempfile

# some change

# --- Page Configuration ---

st.set_page_config(

    page_title="Cloq | Secure Execution Platform",

    page_icon="🔒",

    layout="wide"

)



# --- Custom CSS for Styling ---

st.markdown("""

<style>

    /* General styling */

    .stApp {

        background-color: #f0f2f6;

    }

    /* Set default text color for the app */

    body, .stApp, .stMarkdown, .stTabs, p, div, span {

        color: #333333;

    }

    h1 {

        color: #1a1a1a !important;

        font-weight: 600;

    }

    h2, h3 {

        color: #333333 !important;

        font-weight: 500;

    }

    .stButton>button {

        border-radius: 8px;

        border: 1px solid #1a1a1a;

        background-color: #ffffff;

        color: #1a1a1a;

        font-weight: 600;

        transition: all 0.2s ease-in-out;

    }

    .stButton>button:hover {

        background-color: #e9ecef;

        color: #1a1a1a;

        border-color: #1a1a1a;

    }

    /* Tab styling */

    .stTabs [data-baseweb="tab-list"] {

        gap: 24px;

        border-bottom: 2px solid #e0e0e0;

    }

    .stTabs [data-baseweb="tab"] {

        height: 50px;

        white-space: pre-wrap;

        background-color: transparent;

        border: none;

        padding-top: 10px;

        padding-bottom: 10px;

    }

    .stTabs [aria-selected="true"] {

        background-color: transparent;

        color: #1a1a1a; /* Ensure selected tab text is dark */

        border-bottom: 2px solid #1a1a1a;

    }

    /* Style the file uploader - AGGRESSIVE OVERRIDE */

    [data-testid="stFileUploader"] section {

        background-color: #fafafa !important;

        border: 2px dashed #cccccc !important;

        border-radius: 8px;

    }

    [data-testid="stFileUploader"] section * {

        color: #333333 !important;

    }

    [data-testid="stFileUploader"] svg {

        fill: #333333 !important;

    }

    [data-testid="stFileUploader"] button {

        border-color: #cccccc !important;

        background-color: #e0e0e0 !important;

        color: #333333 !important;

    }

    /* Style text inputs and text areas - AGGRESSIVE OVERRIDE */

    [data-testid="stTextInput"] input, 

    [data-testid="stTextArea"] textarea {

        background-color: #ffffff !important;

        border: 1px solid #cccccc !important;

        border-radius: 8px !important;

        padding: 10px !important;

        color: #333333 !important;

    }

</style>

""", unsafe_allow_html=True)





# --- Simulated Cryptographic Functions ---

def generate_key():

    return os.urandom(16)



def encrypt(data, key):

    return bytes([b ^ k for b, k in zip(data, key * (len(data) // len(key) + 1))])



def decrypt(data, key):

    return bytes([b ^ k for b, k in zip(data, key * (len(data) // len(key) + 1))])





# --- Main Application Title ---

st.title("Cloq: Secure Execution Platform")





# --- Tab Definitions ---

control_plane_tab, vendor_tab, enterprise_tab = st.tabs(

    ["Control Plane", "SaaS Vendor", "Enterprise Consumer"]

)





# --- Control Plane Tab ---

with control_plane_tab:

    st.header("Control Plane Interaction")

    st.info(

        """

        This tab allows you to interact directly with the Cloq Control Plane API.

        **Note:** The control plane server must be running for these operations to succeed.

        Start it with: `python -m src.cloq_cp.main`

        """

    )



    base_url = "http://localhost:8000"



    # Section 1: Health Check

    st.subheader("1. Health Check")

    if st.button("Check Server Health"):

        with st.spinner("Pinging control plane..."):

            try:

                response = requests.get(f"{base_url}/health", timeout=5)

                if response.status_code == 200:

                    health_data = response.json()

                    st.success("Control plane is healthy!")

                    st.json(health_data)

                else:

                    st.error(f"Health check failed. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane. Is it running?")

            except Exception as e:

                st.error(f"An unexpected error occurred: {e}")



    # Section 2: Upload Artifact

    st.subheader("2. Upload Artifact")

    artifact_content = st.text_area("Enter content for a new artifact:", "This is a test artifact for the Cloq control plane.", height=100)

    if st.button("Create and Upload Artifact"):

        with st.spinner("Uploading artifact..."):

            try:

                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:

                    f.write(artifact_content)

                    temp_file_path = f.name

                

                with open(temp_file_path, 'rb') as f:

                    files = {'file': ('test_artifact.txt', f, 'text/plain')}

                    response = requests.post(f"{base_url}/upload", files=files)

                

                os.unlink(temp_file_path)



                if response.status_code == 200:

                    upload_data = response.json()

                    st.success("Artifact uploaded successfully!")

                    st.session_state.last_artifact_id = upload_data.get('artifact_id')

                    st.json(upload_data)

                else:

                    st.error(f"Upload failed. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane.")

            except Exception as e:

                st.error(f"An unexpected error occurred during upload: {e}")



    # Section 3: List Artifacts

    st.subheader("3. List Artifacts")

    if st.button("Get Artifact List"):

        with st.spinner("Fetching artifact list..."):

            try:

                response = requests.get(f"{base_url}/list")

                if response.status_code == 200:

                    st.success("Artifact list retrieved.")

                    st.json(response.json())

                else:

                    st.error(f"Failed to get list. Status code: {response.status_code}")

                    st.text(response.text)

            except requests.exceptions.ConnectionError:

                st.error("Connection Error: Could not connect to the control plane.")

            except Exception as e:

                st.error(f"An unexpected error occurred: {e}")



    # Section 4: Download Artifact

    st.subheader("4. Download Artifact")

    default_id = st.session_state.get('last_artifact_id', '')

    artifact_id_to_download = st.text_input("Enter Artifact ID to download:", value=default_id)

    if st.button("Download Artifact"):

        if not artifact_id_to_download:

            st.warning("Please enter an Artifact ID.")

        else:

            with st.spinner(f"Downloading artifact {artifact_id_to_download}..."):

                try:

                    response = requests.get(f"{base_url}/download/{artifact_id_to_download}")

                    if response.status_code == 200:

                        st.success("Download successful!")

                        st.text("File Content:")

                        st.code(response.text, language="")

                    else:

                        st.error(f"Download failed. Status code: {response.status_code}")

                        st.text(response.text)

                except requests.exceptions.ConnectionError:

                    st.error("Connection Error: Could not connect to the control plane.")

                except Exception as e:

                    st.error(f"An unexpected error occurred: {e}")





# --- SaaS Vendor Tab ---

with vendor_tab:

    st.header("Vendor: Seal and Publish")

    st.write(

        """

        As the SaaS Vendor, you will seal your proprietary code into an encrypted container 

        layer and publish it to a secure registry.

        """

    )



    st.subheader("Step 1: Upload and Seal Proprietary Code")

    uploaded_file = st.file_uploader("Upload your proprietary code/data (e.g., a .py or .txt file)", key="vendor_uploader")



    if uploaded_file is not None:

        if "sealed" not in st.session_state:

            st.session_state.sealed = False



        if not st.session_state.sealed:

            if st.button("Seal and Publish"):

                with st.spinner("Sealing proprietary code..."):

                    proprietary_data = uploaded_file.getvalue()

                    st.session_state.original_data = proprietary_data



                    data_encryption_key = generate_key()

                    st.session_state.data_encryption_key = data_encryption_key



                    sealed_layer = encrypt(proprietary_data, data_encryption_key)

                    st.session_state.sealed_layer = sealed_layer



                    st.session_state.wrapped_key = data_encryption_key 

                    st.session_state.sealed = True

                st.success("Proprietary code sealed and published successfully!")



        if st.session_state.sealed:

            st.subheader("Published Artifacts")

            st.write("These artifacts are now available in the secure registry.")

            

            st.write("**Sealed Image Layer (Encrypted):**")

            st.code(st.session_state.sealed_layer.hex(), language="")



            st.write("**Wrapped Execution Key:**")

            st.code(st.session_state.wrapped_key.hex(), language="")

            

            st.info("Navigate to the **Enterprise Consumer** tab to proceed with secure execution.")

    else:

        st.info("Please upload a file to begin the sealing process.")





# --- Enterprise Consumer Tab ---

with enterprise_tab:

    st.header("Enterprise: Securely Execute Software")

    st.write(

        """

        As the Enterprise Consumer, you will attest your environment, retrieve the sealed 

        container, and execute it securely.

        """

    )



    if "sealed" not in st.session_state or not st.session_state.sealed:

        st.warning("The SaaS Vendor has not published a sealed image yet. Please go to the **SaaS Vendor** tab first.")

    else:

        st.subheader("Step 1: Remote Attestation")

        st.write("The execution environment must prove its integrity to the Compliance Service.")



        if "attested" not in st.session_state:

            st.session_state.attested = False



        if not st.session_state.attested:

            if st.button("Perform Remote Attestation"):

                with st.spinner("Performing attestation..."):

                    time.sleep(1)

                    st.session_state.attested = True

                st.success("Attestation successful! Environment is trusted.")



        if st.session_state.attested:

            st.subheader("Step 2: Retrieve and Unwrap Execution Key")

            st.write("The Compliance Service has released the wrapped key.")



            if "unwrapped" not in st.session_state:

                st.session_state.unwrapped = False



            if not st.session_state.unwrapped:

                if st.button("Unwrap Execution Key"):

                    with st.spinner("Unwrapping key with private key..."):

                        time.sleep(1)

                        st.session_state.execution_key = st.session_state.wrapped_key

                        st.session_state.unwrapped = True

                    st.success("Execution Key ($K_D$) successfully retrieved!")



            if st.session_state.unwrapped:

                st.write("**Retrieved Execution Key ($K_D$):**")

                st.code(st.session_state.execution_key.hex(), language="")



                st.subheader("Step 3: In-Memory Unseal and Run")

                st.write("The sealed layer is decrypted and loaded directly into memory.")



                if st.button("Unseal and Run"):

                    with st.spinner("Decrypting layer and executing in memory..."):

                        time.sleep(1)

                        decrypted_data = decrypt(st.session_state.sealed_layer, st.session_state.execution_key)

                        

                        st.success("Container running! Proprietary code is now executing in a secure environment.")

                        

                        st.subheader("Result: Captured Output from Executed Code")

                        

                        output_capture = io.StringIO()

                        try:

                            with contextlib.redirect_stdout(output_capture):

                                exec(decrypted_data.decode('utf-8'))

                            captured_output = output_capture.getvalue()

                            st.write("The following output was captured from the code running in memory:")

                            st.code(captured_output, language="")

                        except Exception as e:

                            st.error(f"An error occurred during execution: {e}")



                        st.balloons()

                        st.info("The decrypted code was executed in memory and **never** written to disk on the enterprise side.")

