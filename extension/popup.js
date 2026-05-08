let latestReport = "";

document.getElementById("analyzeBtn").addEventListener("click", async () => {

    const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    chrome.tabs.sendMessage(
        tab.id,
        { action: "getEmail" },

        async (response) => {

            if (!response || !response.email) {

                document.getElementById("result").innerHTML =
                    "Could not detect email content.";

                return;
            }

            const apiResponse = await fetch("http://127.0.0.1:5000/analyze", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: response.email
                })
            });

            const data = await apiResponse.json();

            const resultDiv = document.getElementById("result");

resultDiv.innerHTML =
    `Verdict: ${data.verdict}<br>Risk Score: ${data.score}`;

if (data.verdict.includes("High")) {
    resultDiv.style.borderLeft = "6px solid red";
}
else if (data.verdict.includes("Medium")) {
    resultDiv.style.borderLeft = "6px solid orange";
}
else {
    resultDiv.style.borderLeft = "6px solid green";
}

            const reasonsList = document.getElementById("reasons");

            reasonsList.innerHTML = "";

            data.reasons.forEach(reason => {

                const li = document.createElement("li");

                li.textContent = reason;

                reasonsList.appendChild(li);
            });

            latestReport = `
PHISHING EMAIL ANALYSIS REPORT
================================

Subject:
${response.subject}

Sender:
${response.sender}

Verdict:
${data.verdict}

Risk Score:
${data.score}

Reasons:
${data.reasons.join("\n")}

Recommended Actions:
- Do not click suspicious links
- Verify sender identity
- Avoid sharing credentials
- Report suspicious email
`;
        }
    );
});


document.getElementById("downloadBtn").addEventListener("click", () => {

    const blob = new Blob([latestReport], {
        type: "text/plain"
    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = "phishing_report.txt";

    a.click();

    URL.revokeObjectURL(url);
});