const server_url = "http://127.0.0.1:8000/";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "review_check",
    title: "Review Check",
    contexts: ["selection"], // Show the menu on selected text
  });
  console.log("Extension installed and context menu created.");
});

// Function to handle popup messages
function handlePopupMessage(res) {
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = ''; // Clear any previous content in resultDiv

  if (res.message === "Analyzing...") {
    resultDiv.textContent = res.message; // Show "Analyzing..." message while the result is being fetched
  } else if (res.message === "Analysis completed.") {
    const analysisData = res.analysis;

    const createLabeledContent = (labelText, contentText) => {
      const container = document.createElement('div');
      const header = document.createElement('div');
      header.classList.add('label');
      header.textContent = `${labelText}:`;

      const content = document.createElement('div');
      content.classList.add('content');
      content.textContent = contentText || 'None'; // Default to "None" if content is missing

      container.appendChild(header);
      container.appendChild(content);

      return container;
    };

    // Add the analysis data to the popup
    resultDiv.appendChild(createLabeledContent('Verdict', analysisData.verdict));
    resultDiv.appendChild(createLabeledContent('Confidence', analysisData.confidence));
    resultDiv.appendChild(createLabeledContent('Explanation', analysisData.explanation));
    resultDiv.appendChild(createLabeledContent('Key Points', analysisData.key_points.join(', ')));
    resultDiv.appendChild(createLabeledContent('Evidence Quality', analysisData.evidence_quality.overall_assessment));
    resultDiv.appendChild(createLabeledContent('Source Consensus', analysisData.source_consensus.description));
    resultDiv.appendChild(createLabeledContent('Supporting Evidence', analysisData.supporting_evidence.join(', ')));

    // Optionally, log the received result for debugging purposes
    console.log('Received analysis result:', analysisData);
  }
}

// Listen for context menu clicks
chrome.contextMenus.onClicked.addListener((clickData) => {
  if (clickData.menuItemId === "review_check" && clickData.selectionText) {
    const selectedText = clickData.selectionText.trim();
    console.log("Selected text for analysis:", selectedText);

    // Create a popup window with a message that the review is being analyzed
    chrome.windows.create({
      url: "./popup.html", // URL of the popup HTML file
      type: "popup",
      width: 400,
      height: 300,
    }, (window) => {
      // Ensure the window was created successfully
      if (window) {
        let my_data = { message: "Analyzing..." };
        handlePopupMessage(my_data);

        // Make a POST request to the server with the selected review text
        const review_url = `${server_url}api/v1/check/text`;

        fetch(review_url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text: selectedText }),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Server returned status ${response.status}`);
            }
            return response.json();
          })
          .then((data) => {
            console.log("Response from server:", data);

            // Send the result to the popup once the data is received
            let resultData = {
              message: "Analysis completed.",
              analysis: data.response.analysis,
            };
            handlePopupMessage(resultData);
          })
          .catch((error) => {
            console.error("Error communicating with the server:", error);

            // Send error details to the popup if an error occurs
            chrome.runtime.sendMessage({
              action: "showPopup",
              error: error.message,
              windowId: window.id,
            });
          });
      } else {
        console.error("Failed to create popup window");
      }
    });
  }
});


// Listen for context menu clicks
chrome.contextMenus.onClicked.addListener((clickData) => {
  if (clickData.menuItemId === "review_check" && clickData.selectionText) {
    const selectedText = clickData.selectionText.trim();
    console.log("Selected text for analysis:", selectedText);

    // Create the popup window
    chrome.windows.create(
      {
        url: "./popup.html", // URL of the popup HTML file
        type: "popup",
        width: 400,
        height: 300,
      },
      (window) => {
        if (window) {
          // Notify the popup that analysis has started
          chrome.runtime.sendMessage({
            action: "updateAnalysis",
            status: "analyzing",
          });

          // Make a POST request to the server
          const review_url = `${server_url}api/v1/check/text`;

          fetch(review_url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: selectedText }),
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
              }
              return response.json();
            })
            .then((data) => {
              console.log("Response from server:", data);

              // Notify the popup of the completed analysis
              chrome.runtime.sendMessage({
                action: "updateAnalysis",
                status: "completed",
                analysis: data.response.analysis,
              });
            })
            .catch((error) => {
              console.error("Error communicating with the server:", error);
              chrome.runtime.sendMessage({
                action: "updateAnalysis",
                status: "error",
                error: error.message,
              });
            });
        } else {
          console.error("Failed to create popup window");
        }
      }
    );
  }
});
