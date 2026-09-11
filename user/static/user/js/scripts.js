function disp() {
    alert("I calling from course file");
}

document.addEventListener("DOMContentLoaded", function () {
    const chatbotButton = document.getElementById("chatbotButton");
    const openChatbot = document.getElementById("openChatbot");
    const chatbotWindow = document.getElementById("chatbotWindow");
    const closeChatbot = document.getElementById("closeChatbot");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    let fareStep = null;
    let fareData = {
        pickup: "",
        destination: "",
        rideType: ""
    };
    if (!openChatbot || !chatbotButton || !chatbotWindow) {
        console.error("NandiRide Chatbot: Required elements not found.");
        return;
    }
    if (openChatbot.dataset.chatbotReady === "true") {
        return;
    }
    openChatbot.dataset.chatbotReady = "true";
    openChatbot.addEventListener("click", function () {
        chatbotWindow.classList.remove("d-none");
        chatbotButton.classList.add("d-none");
        setTimeout(function () {
            if (chatInput) {
                chatInput.focus();
            }
        }, 150);
    });
    if (closeChatbot) {
        closeChatbot.addEventListener("click", function () {
            chatbotWindow.classList.add("d-none");
            chatbotButton.classList.remove("d-none");
        });
    }
    if (chatForm && chatInput && chatMessages) {
        chatForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const message = chatInput.value.trim();
            if (!message) {
                return;
            }
            chatInput.value = "";
            if (fareStep) {
                handleFareInput(message);
                return;
            }
            addUserMessage(message);
            showBotReply(message);
        });
    }
    window.sendBotMessage = function (message) {
        if (!chatMessages) {
            return;
        }
        addUserMessage(message);
        showBotReply(message);
    };
    window.startFareEstimate = function () {
        if (!chatMessages) {
            return;
        }
        addUserMessage("Fare Estimate");
        startFareFlow();
    };
    window.selectFareRide = function (rideType) {
        fareData.rideType = rideType;
        addUserMessage(rideType);
        fareStep = null;
        if (chatInput) {
            chatInput.placeholder = "Type your message...";
        }
        showTyping();
        setTimeout(function () {
            removeTyping();
            calculateFare();
        }, 700);
    };
    window.startNewFareEstimate = function () {
        fareData = {
            pickup: "",
            destination: "",
            rideType: ""
        };
        startFareFlow();
    };
    function addUserMessage(message) {
        const messageWrapper = document.createElement("div");
        messageWrapper.className = "d-flex justify-content-end mb-3";
        messageWrapper.innerHTML = `
            <div class="bg-danger text-white shadow-sm rounded-4 rounded-top-end-0 px-3 py-2" style="max-width:80%;">
                <p class="mb-0 small">${escapeHtml(message)}</p>
            </div>
        `;
        chatMessages.appendChild(messageWrapper);
        scrollChat();
    }
    function addBotMessage(message) {
        const messageWrapper = document.createElement("div");
        messageWrapper.className = "d-flex align-items-start mb-3";
        messageWrapper.innerHTML = `
            <div class="bg-danger text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 me-2" style="width:36px;height:36px;">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="bg-white shadow-sm rounded-4 rounded-top-start-0 px-3 py-2" style="max-width:85%;">
                <p class="mb-0 small text-secondary">${message}</p>
            </div>
        `;
        chatMessages.appendChild(messageWrapper);
        scrollChat();
    }
    function showTyping() {
        removeTyping();
        const typing = document.createElement("div");
        typing.id = "chatTyping";
        typing.className = "d-flex align-items-start mb-3";
        typing.innerHTML = `
            <div class="bg-danger text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 me-2" style="width:36px;height:36px;">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="bg-white shadow-sm rounded-4 rounded-top-start-0 px-3 py-2">
                <span class="text-secondary small">
                    <i class="fa-solid fa-circle-notch fa-spin me-1"></i>
                    Typing...
                </span>
            </div>
        `;
        chatMessages.appendChild(typing);
        scrollChat();
    }
    function removeTyping() {
        const typing = document.getElementById("chatTyping");
        if (typing) {
            typing.remove();
        }
    }
    function showBotReply(message) {
        const text = message.toLowerCase().trim();
        if (
            text.includes("fare") ||
            text.includes("price") ||
            text.includes("cost") ||
            text.includes("rate") ||
            text.includes("kiraya") ||
            text.includes("किराया")
        ) {
            startFareFlow();
            return;
        }
        showTyping();
        setTimeout(function () {
            removeTyping();
            let reply = `
                😊 I can help you with:
                <br><br>
                🚕 Book a Ride<br>
                💰 Fare Estimate<br>
                📍 Track Ride<br>
                ❌ Cancel Ride<br>
                📋 My Rides<br>
                💳 Payment
            `;
            if (
                text.includes("hello") ||
                text.includes("hi") ||
                text.includes("hii") ||
                text.includes("hey") ||
                text.includes("नमस्ते")
            ) {
                reply = `
                    👋 Hello! Welcome to <strong>NandiRide</strong>.
                    <br><br>
                    मैं आपकी ride booking और ride services में help कर सकता हूँ. 😊
                    <br><br>
                    आप क्या करना चाहते हैं?
                `;
            } else if (
                text.includes("book") ||
                text.includes("booking") ||
                text.includes("ride book") ||
                text.includes("बुक")
            ) {
                reply = `
                    🚕 <strong>Let's book your NandiRide!</strong>
                    <br><br>
                    अपनी pickup और destination location डालकर ride book करें.
                    <br><br>
                    <a href="${chatbotUrls.booking}" class="btn btn-danger btn-sm rounded-pill px-3">
                        <i class="fa-solid fa-taxi me-1"></i>
                        Book a Ride
                    </a>
                `;
            } else if (
                text.includes("track") ||
                text.includes("tracking") ||
                text.includes("location") ||
                text.includes("where is my ride") ||
                text.includes("ride kaha") ||
                text.includes("ride kahan") ||
                text.includes("कहाँ") ||
                text.includes("कहा")
            ) {
                reply = `
                    📍 <strong>Track Your Ride</strong>
                    <br><br>
                    अपनी current ride की location और status देखने के लिए नीचे button दबाएँ.
                    <br><br>
                    <a href="${chatbotUrls.track}" class="btn btn-danger btn-sm rounded-pill px-3">
                        <i class="fa-solid fa-location-dot me-1"></i>
                        Track Ride
                    </a>
                `;
            } else if (
                text.includes("cancel") ||
                text.includes("cancellation") ||
                text.includes("cancel ride") ||
                text.includes("cancel kar") ||
                text.includes("रद्द")
            ) {
                reply = `
                    ❌ <strong>Cancel Ride</strong>
                    <br><br>
                    अगर आप अपनी active ride cancel करना चाहते हैं तो नीचे button दबाएँ.
                    <br><br>
                    <a href="${chatbotUrls.cancel}" class="btn btn-danger btn-sm rounded-pill px-3">
                        <i class="fa-solid fa-ban me-1"></i>
                        Cancel Ride
                    </a>
                `;
            } else if (
                text.includes("my ride") ||
                text.includes("my rides") ||
                text.includes("ride history") ||
                text.includes("history") ||
                text.includes("meri ride") ||
                text.includes("meri rides") ||
                text.includes("मेरी ride") ||
                text.includes("मेरी राइड")
            ) {
                reply = `
                    📋 <strong>My Rides</strong>
                    <br><br>
                    यहाँ आप अपनी previous और current rides देख सकते हैं.
                    <br><br>
                    <a href="${chatbotUrls.myride}" class="btn btn-danger btn-sm rounded-pill px-3">
                        <i class="fa-solid fa-clock-rotate-left me-1"></i>
                        View My Rides
                    </a>
                `;
            } else if (
                text.includes("payment") ||
                text.includes("pay") ||
                text.includes("paid") ||
                text.includes("payment status") ||
                text.includes("भुगतान")
            ) {
                reply = `
                    💳 <strong>Payment</strong>
                    <br><br>
                    अपने ride payment details और payment status देखने के लिए नीचे button दबाएँ.
                    <br><br>
                    <a href="${chatbotUrls.payment}" class="btn btn-danger btn-sm rounded-pill px-3">
                        <i class="fa-solid fa-credit-card me-1"></i>
                        Payment
                    </a>
                `;
            } else if (
                text.includes("help") ||
                text.includes("support") ||
                text.includes("madad") ||
                text.includes("मदद")
            ) {
                reply = `
                    😊 <strong>I'm here to help!</strong>
                    <br><br>
                    आप मुझसे पूछ सकते हैं:
                    <br><br>
                    🚕 Book my ride<br>
                    💰 What is the fare?<br>
                    📍 Track my ride<br>
                    ❌ Cancel my ride<br>
                    📋 Show my rides<br>
                    💳 Payment status
                `;
            } else if (
                text.includes("thank") ||
                text.includes("thanks") ||
                text.includes("धन्यवाद")
            ) {
                reply = `
                    😊 You're welcome!
                    <br><br>
                    <strong>NandiRide</strong> is always happy to help you. 🚕❤️
                `;
            } else if (
                text.includes("bye") ||
                text.includes("goodbye")
            ) {
                reply = `
                    👋 Goodbye!
                    <br><br>
                    Thank you for choosing <strong>NandiRide</strong>. Have a safe journey! 🚕❤️
                `;
            }
            addBotMessage(reply);
        }, 700);
    }
    function startFareFlow() {
        fareData = {
            pickup: "",
            destination: "",
            rideType: ""
        };
        showTyping();
        setTimeout(function () {
            removeTyping();
            addBotMessage(`
                💰 <strong>Let's calculate your estimated fare!</strong>
                <br><br>
                पहले अपना <strong>Pickup Location</strong> बताइए.
            `);
            setFareStep("pickup");
        }, 500);
    }
    function setFareStep(step) {
        fareStep = step;
        if (chatInput) {
            if (step === "pickup") {
                chatInput.placeholder = "Enter pickup location...";
            } else if (step === "destination") {
                chatInput.placeholder = "Enter destination...";
            } else {
                chatInput.placeholder = "Type your message...";
            }
            chatInput.focus();
        }
    }
    function handleFareInput(message) {
        if (fareStep === "pickup") {
            fareData.pickup = message;
            addUserMessage(message);
            addBotMessage(`
                📍 <strong>Pickup:</strong> ${escapeHtml(message)}
                <br><br>
                अब अपना <strong>Destination</strong> बताइए.
            `);
            setFareStep("destination");
            return;
        }
        if (fareStep === "destination") {
            fareData.destination = message;
            addUserMessage(message);
            addBotMessage(`
                📍 <strong>Destination:</strong> ${escapeHtml(message)}
                <br><br>
                अब अपना <strong>Ride Type</strong> चुनें:
                <br><br>
                <button type="button" class="btn btn-outline-danger btn-sm rounded-pill me-1 mb-1" onclick="selectFareRide('Bike')">
                    🏍️ Bike
                </button>
                <button type="button" class="btn btn-outline-danger btn-sm rounded-pill me-1 mb-1" onclick="selectFareRide('Auto')">
                    🛺 Auto
                </button>
                <button type="button" class="btn btn-outline-danger btn-sm rounded-pill mb-1" onclick="selectFareRide('Sedan')">
                    🚗 Sedan
                </button>
            `);
            setFareStep("ride");
            return;
        }
        if (fareStep === "ride") {
            const ride = normalizeRideType(message);
            if (!ride) {
                addUserMessage(message);
                addBotMessage(`
                    ⚠️ Please select a valid ride type:
                    <br><br>
                    🏍️ Bike &nbsp; 🛺 Auto &nbsp; 🚗 Sedan
                `);
                return;
            }
            selectFareRide(ride);
        }
    }
    function normalizeRideType(message) {
        const text = message.toLowerCase().trim();
        if (text.includes("bike") || text.includes("बाइक")) {
            return "Bike";
        }
        if (text.includes("auto") || text.includes("ऑटो")) {
            return "Auto";
        }
        if (
            text.includes("sedan") ||
            text.includes("cab") ||
            text.includes("car") ||
            text.includes("सेडान")
        ) {
            return "Sedan";
        }
        return null;
    }
    function calculateFare() {
        let baseFare = 0;
        let perKm = 0;
        let estimatedDistance = 5;
        if (fareData.rideType === "Bike") {
            baseFare = 20;
            perKm = 8;
        } else if (fareData.rideType === "Auto") {
            baseFare = 30;
            perKm = 12;
        } else if (fareData.rideType === "Sedan") {
            baseFare = 50;
            perKm = 18;
        }
        const distanceFare = estimatedDistance * perKm;
        const totalFare = baseFare + distanceFare;
        addBotMessage(`
            🧾 <strong>Estimated Fare</strong>
            <br><br>
            <div class="bg-light rounded-3 p-3">
                <div class="d-flex justify-content-between mb-2 gap-2">
                    <span>📍 Pickup</span>
                    <strong class="text-end">${escapeHtml(fareData.pickup)}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2 gap-2">
                    <span>📍 Destination</span>
                    <strong class="text-end">${escapeHtml(fareData.destination)}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>🚕 Ride</span>
                    <strong>${fareData.rideType}</strong>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>📏 Distance</span>
                    <strong>${estimatedDistance} km</strong>
                </div>
                <hr>
                <div class="d-flex justify-content-between">
                    <span class="fw-bold">Estimated Fare</span>
                    <strong class="text-danger fs-5">₹${totalFare}</strong>
                </div>
            </div>
            <small class="text-muted d-block mt-2">
                * Demo estimate. Actual fare may vary according to distance, traffic and waiting time.
            </small>
            <div class="mt-3">
                <a href="${chatbotUrls.booking}" class="btn btn-danger btn-sm rounded-pill px-3">
                    <i class="fa-solid fa-taxi me-1"></i>
                    Book This Ride
                </a>
                <button type="button" class="btn btn-outline-danger btn-sm rounded-pill px-3 ms-1" onclick="startNewFareEstimate()">
                    Calculate Again
                </button>
            </div>
        `);
    }
    function scrollChat() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
});