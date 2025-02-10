import streamlit as st
import requests
import io
import base64
import os
from PIL import Image
from dotenv import load_dotenv
import streamlit.components.v1 as components  # Import for HTML execution

# Load environment variables
load_dotenv()
# OCR_API_KEY = os.getenv("OCR_API_KEY") # local
OCR_API_KEY = st.secrets["OCR_API_KEY"] # streamlit

# Load Logo
try:
    icon = Image.open("./frontend/logo.png")
except FileNotFoundError:
    st.error("Logo image not found. Please place 'logo.png' in the 'frontend' directory.")
    st.stop()

# Utility Functions
def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def image_to_text(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("image.png", img_bytes)},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()
    return result["ParsedResults"][0]["ParsedText"].strip() if result["OCRExitCode"] == 1 else "Error: Unable to extract text."

# Streamlit App
st.set_page_config(page_title="Valid8", page_icon=icon, layout="centered")

# st.markdown("---")
# st.markdown(
#     """
#     <div style='text-align: center'>
#         <span>To use our Chrome Extension:</span> <a href="https://github.com/Psingle20/Valid8rs" style='font-size: 1.2rem'> 🚀 GitHub</a>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

def display_analysis_results(data):
    """Displays the structured fact-check analysis in a well-formatted way."""

    if not data or "results" not in data:
        st.error("Invalid or empty analysis data.")
        return

    results = data["results"]

    if "analysis" in results:
        analysis = results["analysis"]
        st.success("Analysis Complete! 🎉")

        # Verdict
        st.markdown(f"<div class='result-card'><span class='heading verdict'>Verdict:</span> {analysis.get('verdict', 'N/A')}</div>", unsafe_allow_html=True)

        # Confidence
        st.markdown(f"<div class='result-card'><span class='heading confidence'>Confidence:</span> {analysis.get('confidence', 'N/A')}</div>", unsafe_allow_html=True)

        # Explanation
        st.markdown(f"<div class='result-card'><span class='heading explanation'>Explanation:</span> {analysis.get('explanation', 'N/A')}</div>", unsafe_allow_html=True)

        # Key Considerations
        key_considerations = analysis.get('fact_check_summary', {}).get('key_considerations', [])
        if key_considerations:
            considerations_text = "<ul>" + "".join([f"<li>{consideration}</li>" for consideration in key_considerations]) + "</ul>"
            st.markdown(f"<div class='result-card '><span class='heading consideration'>Key Considerations:</span> {considerations_text}</div>", unsafe_allow_html=True)

        # Evaluated Sources & Scores
        evaluated_sources = results.get("evaluated_sources", [])
        if evaluated_sources:
            reliability_score = evaluated_sources[0].get("reliability_score", "N/A")
            relevance_score = evaluated_sources[0].get("relevance_score", "N/A")
            st.markdown(f"""
                <div class='result-card'>
                    <b class='heading'>Scores:</b><br>
                    <span class='score-box reliability'>Reliability Score: {reliability_score}</span>
                    <span class='score-box relevance'>Relevance Score: {relevance_score}</span>
                </div>
            """, unsafe_allow_html=True)

        # Supporting Evidence
        supporting_evidence = analysis.get('supporting_evidence', [])
        if supporting_evidence:
            evidence_list = "<ul>" + "".join([f"<li><a href='{url}'>{url}</a></li>" for url in supporting_evidence]) + "</ul>"
            st.markdown(f"<div class='result-card'><b class='heading'>Supporting Evidence:</b> {evidence_list}</div>", unsafe_allow_html=True)

        # Evidence Analysis Section
        evidence_quality = analysis.get('evidence_quality', {})
        overall_assessment = evidence_quality.get('overall_assessment', 'N/A')
        strength_of_evidence = evidence_quality.get('strength_of_evidence', 'N/A')
        consistency_across_sources = evidence_quality.get('consistency_across_sources', 'N/A')
        source_consensus = analysis.get('source_consensus', {}).get('description', 'N/A')

        st.markdown(f"""
            <div class='result-card '>
                <b class='evidence-analysis heading'>Evidence Analysis:</b><br>
                <b>Overall Quality:</b> {overall_assessment}<br>
                <b>Strength of Evidence:</b> {strength_of_evidence}<br>
                <b>Consistency Across Sources:</b> {consistency_across_sources}<br>
                <b>Source Consensus:</b> {source_consensus}
            </div>
        """, unsafe_allow_html=True)

        # Limitations
        limitations = analysis.get('limitations', [])
        if limitations:
            limitations_text = "<ul>" + "".join([f"<li>{limitation}</li>" for limitation in limitations]) + "</ul>"
            st.markdown(f"<div class='result-card '><span class='heading limitations'>Limitations:</span> {limitations_text}</div>", unsafe_allow_html=True)

        # Fact Check Summary
        summary = analysis.get('fact_check_summary', {}).get('main_conclusion', 'N/A')
        st.markdown(f"<div class='result-card'><b class='heading main_conclusion'>Summary:</b> {summary}</div>", unsafe_allow_html=True)


# Initialize session state for SSE trigger
if "sse_started" not in st.session_state:
    st.session_state.sse_started = False

# Styling
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Karla:wght@400;700&display=swap');
        body { font-family: 'Karla', sans-serif; letter-spacing: 0.5px; line-height: 1.6; }
        .main-title { font-size: 3em; font-weight: bold; color: #FFFFFF; text-align: center; }
        .sub-title { font-size: 1.2em; text-align: center; margin-bottom: 20px; color: #555; }
        .result-card {
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 10px;
            }
            .fun-text {
                text-align: center;
                font-style: italic;
                color: #4EB4DC;
            }
            .heading {
                font-size: 1.5em; /* Font size for headings */
                font-weight: bold; /* Bold for emphasis */
            }
            .verdict {
                color: #4CAF50; /* Green for positive verdicts */
            }
            .confidence {
                color: #2196F3; /* Blue for confidence level */
            }
            .explanation {
                color: #FFFF80; /* Grey for explanations */
            }
            .summary {
                color: #FF8F00; /* Summary color */
            }
            .limitations {
                color: #FFBB64; /* Limitations color */
            }
            .evidence-analysis {
                color: #836FFF; /* Evidence analysis color */
            }
            .consideration {
                color: #AED2FF;
            }
            .score-analysis {
                color: #CDC1FF; /* Score analysis color */
            }
            
            .score-box {
                font-size: 1.5rem; /* Makes the score numbers big */
                font-weight: bold; /* Makes the text bold */
                color: white; /* White text color */
                padding: 2px 4px; /* Adds padding for a button-like effect */
                border-radius: 8px; /* Rounds the corners */
                display: inline-block; /* Ensures it doesn't take the full width */
                text-align: center;
                margin: 4px 2px;
            }

            .reliability {
                background: #ff5733; /* Bright reddish-orange for attention */
                box-shadow: 0px 4px 10px rgba(255, 87, 51, 0.5);
            }

            .relevance {
                background: #33c3ff; /* Bright blue for contrast */
                box-shadow: 0px 4px 10px rgba(51, 195, 255, 0.5);
            }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown(
    f"""
    <div style='text-align:center;'>
        <img src="data:image/png;base64,{base64.b64encode(img_to_bytes(icon)).decode('utf-8')}" style='max-height:75px; margin-bottom: 10px; '/>
        <span class='main-title' style ='padding-top: 10px;'>Valid8</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div class='sub-title fun-text'>The internet is full of nonsense — let’s clean it up!🤷‍♀️🚀</div>", unsafe_allow_html=True)

# Fact-Check Options
check_type = st.radio("What would you like to fact-check?", ["Text", "Tweet", "Image"])

# Terminal for Logs (Initially Hidden)

log_container = st.empty()

# Button Click Handler (Starts SSE Logs)
def start_logs():
    st.markdown("### 🔍 Live Logs")
    log_container = st.empty()

    components.html(
        """
        <div id="log-container" style="background: black; color: green; padding: 10px; font-family: monospace; height: 250px; overflow-y: auto; border-radius: 5px; white-space: pre-wrap;"></div>

        <script>
            console.log("Starting SSE...");
            const eventSource = new EventSource("https://web-production-4c842.up.railway.app/api/v1/logs");

            eventSource.onmessage = (event) => {
                console.log("Log:", event.data);
                const logContainer = document.getElementById("log-container");
                logContainer.innerText += event.data + "\\n";
                logContainer.scrollTop = logContainer.scrollHeight; // Auto-scroll
            };

            eventSource.onerror = (error) => {
                console.error("EventSource failed:", error);
            };
        </script>
        """,
        height=300,
    )

# Tweet Fact-Check
if check_type == "Tweet":
    tweet_input = st.text_input("Enter Tweet ID or Tweet URL:", placeholder="Enter tweet ID or Tweet URL...")
    if st.button("Check Tweet"):
        start_logs()
        with st.spinner("Analyzing tweet... Grab a snack 🍿 while we dig deep!!"):
            try:
                response = requests.post("https://web-production-4c842.up.railway.app/api/v1/check/tweet", json={"tweet_id": tweet_input.split("/")[-1]})
                if response.status_code == 200:
                    data = response.json()
                    # st.success("Analysis Complete!")
                    # st.json(data)
                    display_analysis_results(data)
                    
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")

# Text Fact-Check
elif check_type == "Text":
    text_input = st.text_area("Enter text to fact-check:", placeholder="Type or paste the text...")
    if st.button("Check Text"):
        start_logs()
        with st.spinner("Analyzing text... Grab a snack 🍿 while we dig deep!!"):
            try:
                response = requests.post("https://web-production-4c842.up.railway.app/api/v1/check/text", json={"text": text_input})
                if response.status_code == 200:
                    data = response.json()
                    # st.success("Analysis Complete!")
                    # st.json(data)
                    display_analysis_results(data)
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")

# Image Fact-Check
else:
    image_input = st.file_uploader("Upload an image for text extraction:", type=["png", "jpg", "jpeg"])
    if st.button("Extract and Analyze Image"):
        start_logs()
        with st.spinner("Extracting and Analyzing text from image... Grab a snack 🍿 while we dig deep!!"):
            try:
                image = Image.open(image_input)
                extracted_text = image_to_text(image)
                if extracted_text != "Error: Unable to extract text.":
                    st.success("Text extracted successfully!")
                    st.text_area("Extracted Text", value=extracted_text, height=200)
                    response = requests.post("https://web-production-4c842.up.railway.app/api/v1/check/text", json={"text": extracted_text})
                    if response.status_code == 200:
                        data = response.json()
                        # st.success("Analysis Complete!")
                        # st.json(data)
                        display_analysis_results(data)

                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                else:
                    st.error("Error extracting text from the image.")
            except Exception as e:
                st.error(f"Error processing the image: {str(e)}")



# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <span>To use our Chrome Extension:</span> <a href="https://github.com/Psingle20/Valid8rs" style='font-size: 1.2rem'> 🚀 GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)
