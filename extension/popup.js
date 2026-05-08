let latestData = null;

document.getElementById("analyzeBtn")
.addEventListener("click", async () => {

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

            const apiResponse = await fetch(

                "http://127.0.0.1:5000/analyze",

                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: response.email
                    })
                }
            );

            const data = await apiResponse.json();

            const resultDiv =
                document.getElementById("result");

            resultDiv.innerHTML =
                `Verdict: ${data.verdict}<br>
                 Risk Score: ${data.score}`;


            // RISK COLORS

            if (data.verdict.includes("High")) {

                resultDiv.style.borderLeft =
                    "8px solid red";

                resultDiv.style.background =
                    "#ffe5e5";
            }

            else if (data.verdict.includes("Medium")) {

                resultDiv.style.borderLeft =
                    "8px solid orange";

                resultDiv.style.background =
                    "#fff3e0";
            }

            else {

                resultDiv.style.borderLeft =
                    "8px solid green";

                resultDiv.style.background =
                    "#e8f5e9";
            }


            // REASONS LIST

            const reasonsList =
                document.getElementById("reasons");

            reasonsList.innerHTML = "";

            data.reasons.forEach(reason => {

                const li =
                    document.createElement("li");

                li.textContent = reason;

                reasonsList.appendChild(li);
            });


            // STORE REPORT DATA

            latestData = {

    sender: response.sender,

    subject: response.subject,

    verdict: data.verdict,

    score: data.score,

    reasons: data.reasons
};
        }
    );
});


// PDF DOWNLOAD

document.getElementById("downloadBtn")
.addEventListener("click", async () => {

    if (!latestData) {

        alert("Analyze an email first.");

        return;
    }

    const response = await fetch(

        "http://127.0.0.1:5000/generate_report",

        {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(latestData)
        }
    );

    const blob = await response.blob();

    const url =
        window.URL.createObjectURL(blob);

    const a =
        document.createElement("a");

    a.href = url;

    a.download = "phishing_report.pdf";

    a.click();
});