function getEmailContent() {

    const emailBodies = document.querySelectorAll(".a3s");

    let fullText = "";

    emailBodies.forEach(body => {
        fullText += body.innerText + "\n";
    });

    return fullText.trim();
}

function getSender() {

    const senderElement = document.querySelector("span[email]");

    if (senderElement) {
        return senderElement.getAttribute("email");
    }

    return "Unknown Sender";
}

function getSubject() {

    const subjectElement = document.querySelector("h2");

    if (subjectElement) {
        return subjectElement.innerText;
    }

    return "No Subject";
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "getEmail") {

        sendResponse({

            email: getEmailContent(),

            sender: getSender(),

            subject: getSubject()
        });
    }
});