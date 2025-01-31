import streamlit as st
import requests
import time
from datetime import datetime
from PIL import Image
import io
import base64

try:
    icon = Image.open("./logo.png")
except FileNotFoundError:
    st.error("Logo image not found. Please place 'logo.png' in the 'frontend' directory.")
    st.stop()

def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")  # Or format your image is in
    return buf.getvalue()

def main():
    st.set_page_config(page_title="Valid8", page_icon=icon, layout="centered")

    st.markdown(
        """
        <style>
            /* Importing Karla font from Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Karla:wght@400;700&display=swap');

            body {
                font-family: 'Karla', sans-serif; /* Set the entire body font to Karla */
                letter-spacing: 0.5px; /* Increase letter spacing slightly */
                line-height: 1.6; /* Optional: Adjust line height for better readability */
            }
            .main-title {
                font-size: 2.5em;
                font-weight: bold;
                color: #FF4500;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .main-title img {
                margin-right: 10px;
                max-height: 2em;
            }
            .sub-title {
                font-size: 1.2em;
                text-align: center;
                margin-bottom: 20px;
                color: #555;
            }
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
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Title with Logo
    st.markdown(
        """
        <div style='text-align:center; display:flex; align-items:center; justify-content:center;'>
            <img src="data:image/png;base64,{icon_base64}" style='max-height:80px; margin-right:10px;'/>
            <h1 class='main-title'>Valid8</h1>
        </div>
        """.format(icon_base64=base64.b64encode(img_to_bytes(icon)).decode('utf-8')),
        unsafe_allow_html=True
    )
    st.markdown("<div class='sub-title'>Check your facts & verify your sources!</div>", unsafe_allow_html=True)

    check_type = st.radio("What would you like to fact-check?", ["Tweet", "Text"])
    st.markdown("<p class='fun-text'>Because the internet is full of nonsense. Let's clean it up. 🕵️‍♂️</p>", unsafe_allow_html=True)

    if check_type == "Tweet":
        tweet_input = st.text_input("Enter Tweet ID:", placeholder="Enter tweet ID")

        if st.button("Check Tweet", key="tweet_button"):
            if tweet_input:
                with st.spinner("Analyzing tweet... This might take a hot second. ☕"):
                    try:
                        response = requests.post(
                            "https://web-production-4c842.up.railway.app/api/v1/check/tweet",
                            json={"tweet_id": tweet_input.strip()},
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.success("Analysis Complete! 🎉")

                            if data.get("results"):
                                results = data["results"]
                                # for response in results.get("responses", []):
                                    # st.markdown(f"<div class='result-card'>{response}</div>", unsafe_allow_html=True)
                                if "analysis" in results:
                                    analysis = results["analysis"]
                                    st.markdown("### 🧐 Detailed Analysis")
                                    st.markdown(f"<div class='result-card'><span class='heading verdict'>Verdict:</span> {analysis.get('verdict', 'N/A')}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card'><span class='heading confidence'>Confidence:</span> {analysis.get('confidence', 'N/A')}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card'><span class='heading explanation'>Explanation:</span> {analysis.get('explanation', 'N/A')}</div>", unsafe_allow_html=True)
                                
                                    # Supporting Evidence
                                    supporting_evidence = analysis.get('supporting_evidence', [])
                                    if supporting_evidence:
                                        evidence_list = "<ul>" + "".join([f"<li><a href='{url}'>{url}</a></li>" for url in supporting_evidence]) + "</ul>"
                                        st.markdown(f"<div class='result-card'><b class='heading'>Supporting Evidence:</b> {evidence_list}</div>", unsafe_allow_html=True)

                                    # Limitations and Key Considerations
                                    limitations = analysis.get('limitations', [])
                                    key_considerations = analysis.get('fact_check_summary', {}).get('key_considerations', [])
                                    
                                    limitations_text = "<ul>" + "".join([f"<li>{limitation}</li>" for limitation in limitations]) + "</ul>"
                                    considerations_text = "<ul>" + "".join([f"<li>{consideration}</li>" for consideration in key_considerations]) + "</ul>"
                                    
                                    st.markdown(f"<div class='result-card '><span class='heading limitations'>Limitations:</span> {limitations_text}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card '><span class='heading consideration'>Key Considerations:</span> {considerations_text}</div>", unsafe_allow_html=True)

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
                          
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
            else:
                st.warning("Please enter a tweet ID")
    else:
        text_input = st.text_area("Enter text to fact-check:", placeholder="Type or paste the text you want to verify...")

        if st.button("Check Text", key="text_button"):
            if text_input:
                with st.spinner("Analyzing text... Grab a snack while we dig deep. 🍕"):
                    try:
                        response = requests.post(
                            "https://web-production-4c842.up.railway.app/api/v1/check/text",
                            json={"text": text_input},
                        )
                        if response.status_code == 200:
                            data = response.json()
                            st.success("Analysis Complete! 🚀")
                            
                            if data.get("results"):
                                results = data["results"]
                                # for response in results.get("responses", []):
                                    # st.markdown(f"<div class='result-card'>{response}</div>", unsafe_allow_html=True)
                                
                                if "analysis" in results:
                                    analysis = results["analysis"]
                                    st.markdown("### 🧐 Detailed Analysis")
                                    st.markdown(f"<div class='result-card'><span class='heading verdict'>Verdict:</span> {analysis.get('verdict', 'N/A')}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card'><span class='heading confidence'>Confidence:</span> {analysis.get('confidence', 'N/A')}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card'><span class='heading explanation'>Explanation:</span> {analysis.get('explanation', 'N/A')}</div>", unsafe_allow_html=True)
                                
                                    # Supporting Evidence
                                    supporting_evidence = analysis.get('supporting_evidence', [])
                                    if supporting_evidence:
                                        evidence_list = "<ul>" + "".join([f"<li><a href='{url}'>{url}</a></li>" for url in supporting_evidence]) + "</ul>"
                                        st.markdown(f"<div class='result-card'><b class='heading'>Supporting Evidence:</b> {evidence_list}</div>", unsafe_allow_html=True)

                                    # Limitations and Key Considerations
                                    limitations = analysis.get('limitations', [])
                                    key_considerations = analysis.get('fact_check_summary', {}).get('key_considerations', [])
                                    
                                    limitations_text = "<ul>" + "".join([f"<li>{limitation}</li>" for limitation in limitations]) + "</ul>"
                                    considerations_text = "<ul>" + "".join([f"<li>{consideration}</li>" for consideration in key_considerations]) + "</ul>"
                                    
                                    st.markdown(f"<div class='result-card '><span class='heading limitations'>Limitations:</span> {limitations_text}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div class='result-card '><span class='heading consideration'>Key Considerations:</span> {considerations_text}</div>", unsafe_allow_html=True)

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
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
            else:
                st.warning("Please enter some text to analyze")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <a href="https://github.com/Psingle20/Valid8rs" style='font-size: 1.2rem'">🚀 GitHub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
