const server_url = "https://web-production-4c842.up.railway.app/";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "review_check",
    title: "Check for Misinformation",
    contexts: ["selection"], // Show the menu on selected text
  });
  console.log("Extension installed and context menu created.");
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
        width: 600,
        height: 900,
        left: 100,
        top: 100
      },
      (window) => {
        if (window) {
          // Now we need to send the message once the popup is fully loaded.
          // First, listen for the popup to send a ready message
          chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.action === "popupReady" && sender.tab.windowId === window.id) {
              // Notify the popup that analysis has started
              chrome.runtime.sendMessage({
                action: "updateAnalysis",
                status: "analyzing",
                requestText: selectedText
              });

              // Make a POST request to the server with the selected review text
              const review_url = `${server_url}api/v1/check/text`;

              fetch(review_url, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "Content-Length": selectedText.length.toString(), // Add the content length based on the selected text length
                  "Host": "127.0.0.1:8000", // Add the host of the server
                  "User-Agent": "Mozilla/5.0", // Example User-Agent
                  "Accept-Encoding": "gzip, deflate, br", // Accept encoding types
                  "Connection": "keep-alive", // Connection type
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

                  // Send analysis result to the popup after receiving data from the server
                  chrome.runtime.sendMessage({
                    action: "updateAnalysis",
                    status: "completed",
                    results: {analysis: data.results.analysis},
                    requestText: selectedText
                  });
                })
                .catch((error) => {
                  console.error("Error communicating with the server:", error);
                  // Send error message to the popup if an error occurs
                  chrome.runtime.sendMessage({
                    action: "updateAnalysis",
                    status: "error",
                    error: error.message,
                    requestText: selectedText
                  });
                });
            }
          });
        } else {
          console.error("Failed to create popup window");
        }
      }
    );
  }
});
