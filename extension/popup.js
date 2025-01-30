// Send a message indicating that the popup is ready to receive updates
chrome.runtime.sendMessage({ action: "popupReady" });

// Listen for the analysis status updates
chrome.runtime.onMessage.addListener((message) => {
  const resultDiv = document.getElementById("result");
  const loaderDiv = document.getElementById("loader");
  const cardDiv = document.getElementById("bigCard"); // Get the card element

  if (message.action === "updateAnalysis") {
    if (message.status === "analyzing") {
      console.log("I AM ANALYZINGGGGGGGGG");
      cardDiv.style.display = "none"; // Hide the card during loading
      loaderDiv.style.display = "block";
      cardDiv.classList.add("hidden"); // Hide the card during loading
      // resultDiv.innerHTML = ""; // Clear any previous results
      // resultDiv.innerHTML = `<span class="loading loading-spinner text-primary"></span> Analyzing...`;
    } else if (message.status === "completed") {
      console.log("I AM COMPLETEDDD");
      loaderDiv.style.display = "none"; // Hide the loader
      cardDiv.style.display = "block";
      resultDiv.style.display = "block";
      // Ensure the elements exist before trying to set text content
      const verdict = document.getElementById("verdict");
      const confidence = document.getElementById("confidence");
      const evidenceQuality = document.getElementById("evidence-quality");
      const explanation = document.getElementById("explanation");
      const keyPoints = document.getElementById("key-points");
      const supportingEvidence = document.getElementById("supporting-evidence");
      const sourceConsensus = document.getElementById("source-consensus");

      if (verdict) verdict.textContent = message.results.analysis.verdict;
      if (confidence)
        confidence.textContent = message.results.analysis.confidence;
      if (evidenceQuality)
        evidenceQuality.textContent = message.results.analysis.evidence_quality;
      if (explanation)
        explanation.textContent = message.results.analysis.explanation;
      if (keyPoints)
        keyPoints.textContent = message.results.analysis.key_points.join(", ");
      if (supportingEvidence)
        supportingEvidence.textContent =
          message.results.analysis.supporting_evidence.join(", ");
      if (sourceConsensus)
        sourceConsensus.textContent =
          message.results.analysis.source_consensus.description;
    } else if (message.status === "error") {
      resultDiv.innerHTML = `<p class="text-red-500">Error: ${message.error}</p>`;
    } else {
      console.log("WHAT IS THIS STATUS");
    }
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("themeToggle");
  const body = document.body;

  // Load saved theme from localStorage or set default
  const savedTheme = localStorage.getItem("theme") || "light";
  body.setAttribute("data-theme", savedTheme);

  themeToggle.addEventListener("click", () => {
    const currentTheme = body.getAttribute("data-theme");

    // Toggle between light and dark themes (or more)
    const newTheme = currentTheme === "light" ? "dark" : "light";

    // Apply new theme to body
    body.setAttribute("data-theme", newTheme);

    // Save preference
    localStorage.setItem("theme", newTheme);
  });
});
