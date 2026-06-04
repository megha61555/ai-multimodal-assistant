const chatContainer =
document.getElementById("chatContainer");

/* =========================
   CHAT WINDOW
========================= */

function toggleChat(){

    if(
        chatContainer.style.display === "flex"
    ){
        chatContainer.style.display = "none";
    }else{
        chatContainer.style.display = "flex";
    }   
}

function closeChat(event){

    event.stopPropagation();
    chatContainer.style.display = "none";
}

function minimizeChat(event){

    event.stopPropagation();

    chatContainer.style.height = "80px";
}

function maximizeChat(event){

    event.stopPropagation();

    const chatContainer =
    document.getElementById(
        "chatContainer"
    );
    chatContainer.style.height =
    "650px";

    chatContainer.style.display =
    "flex";

    chatContainer.style.flexDirection =
    "column";
}

/* =========================
   SEND MESSAGE
========================= */

async function sendMessage(){

    const input =
    document.getElementById(
        "message"
    );

    const message =
    input.value.trim();

    // EMPTY CHECK

    if(message === ""){
        return;
    }

    const chatBody =
    document.getElementById(
        "chatBody"
    );

    const sendBtn =
    document.getElementById(
        "sendBtn"
    );

    // =========================
    // USER MESSAGE
    // =========================

    chatBody.innerHTML += `

        <div class="message user-message">

            ${message}

        </div>
    `;

    // AUTO SCROLL

    chatBody.scrollTop =
    chatBody.scrollHeight;

    // CLEAR INPUT

    input.value = "";

    // =========================
    // CHANGE SEND TO PAUSE
    // =========================

    sendBtn.innerHTML = "⏸";

    sendBtn.disabled = true;

    // =========================
    // TYPING INDICATOR
    // =========================

    const typingDiv =
    document.createElement("div");

    typingDiv.classList.add(
        "message",
        "bot-message"
    );

    typingDiv.id = "typing";

    typingDiv.innerHTML = `

        <div class="typing">

            <span></span>
            <span></span>
            <span></span>

        </div>
    `;

    chatBody.appendChild(
        typingDiv
    );

    chatBody.scrollTop =
    chatBody.scrollHeight;

    try{

        // =========================
        // SEND TO BACKEND
        // =========================

        const response =
        await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":
                "application/json"
            },

            body:JSON.stringify({

                message:message
            })
        });

        const data =
        await response.json();

        // REMOVE TYPING

        typingDiv.remove();

        // =========================
        // BOT RESPONSE
        // =========================

        chatBody.innerHTML += `

            <div class="message bot-message">

              <div class="bot-content">

                ${data.response.replace(/\n/g, "<br>")}
              </div>
              <div class="bot-actions">

                   <button
                        class="audio-toggle-btn"
                        onclick="toggleSpeech(this,
                        \`${data.response}\`)"
                    >

                        🔊

                    </button>
                </div>
              

            </div>
        `;

        // =========================
        // SPEAK RESPONSE
        // =========================

       /* speakText(data.response);*/

        // AUTO SCROLL

        chatBody.scrollTop =
        chatBody.scrollHeight;

    }catch(error){

        console.log(error);

        typingDiv.remove();

        chatBody.innerHTML += `

            <div class="message bot-message">

                Error generating response

            </div>
        `;
    }

    // =========================
    // RESTORE SEND BUTTON
    // =========================

    sendBtn.innerHTML = "➤";

    sendBtn.disabled = false;
}

/* =========================
   ENTER KEY
========================= */

document
.getElementById("message")
.addEventListener("keypress",
function(event){

    if(event.key === "Enter"){

        sendMessage();
    }
});

/* =========================
   ATTACHMENT MENU
========================= */

function toggleAttachmentMenu(){

    const menu =
    document.getElementById(
        "attachmentMenu"
    );

    if(menu.style.display === "flex"){

        menu.style.display = "none";

    }else{

        menu.style.display = "flex";
    }
}

/* =========================
   OPEN FILE
========================= */

function openFile(type){

    const fileInput =
    document.getElementById("fileInput");

    if(type === "image"){

        fileInput.accept =
        ".png,.jpg,.jpeg";
    }

    else if(type === "pdf"){

        fileInput.accept =
        ".pdf";
    }

    else if(type === "docx"){

        fileInput.accept =
        ".docx";
    }

    fileInput.click();

    document.getElementById(
        "attachmentMenu"
    ).style.display = "none";
}

/* =========================
   FILE UPLOAD
========================= */

document
.getElementById("fileInput")
.addEventListener(
"change",
async function(){

    const file = this.files[0];

    if(!file){
        return;
    }
    /* =========================
   UPLOADING INDICATOR
========================= */

const uploadingDiv =
document.createElement("div");

uploadingDiv.classList.add(
    "message",
    "bot-message",
    "uploading-message"
);

uploadingDiv.innerHTML = `

    <div class="uploading-container">

        <div class="upload-spinner">

        </div>

        <div>

            Uploading file...

        </div>

    </div>
`;

chatBody.appendChild(
    uploadingDiv
);

chatBody.scrollTop =
chatBody.scrollHeight;

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    try{

        const response =
        await fetch("/upload",{

            method:"POST",

            body:formData
        });

        await response.json();
        uploadingDiv.remove();

        const chatBody =
        document.getElementById("chatBody");

        /* =========================
           IMAGE PREVIEW
        ========================= */

        if(file.type.includes("image")){

            const imageURL =
            URL.createObjectURL(file);

            chatBody.innerHTML += `

                <div class="message user-message">

                    <img
                        src="${imageURL}"
                        class="chat-image"
                    >

                    <div class="file-name">

                        ${file.name}

                    </div>

                </div>
            `;
        }

        /* =========================
           PDF / DOCX PREVIEW
        ========================= */

        else{

            let fileIcon = "📄";

            // PDF

            if(
                file.type ===
                "application/pdf"
            ){

                fileIcon = "📕";
            }

            // DOCX

            else if(
                file.name.endsWith(".docx")
            ){

                fileIcon = "📝";
            }

            // ZIP

            else if(
                file.name.endsWith(".zip")
            ){

                fileIcon = "🗂";
            }

            chatBody.innerHTML += `

                <div class="message user-message file-preview">

                    <div class="file-preview-content">

                        <div class="file-icon">

                            ${fileIcon}

                        </div>

                        <div class="file-details">

                            <div class="file-name">

                                ${file.name}

                            </div>

                            <div class="file-size">

                                ${(file.size / 1024).toFixed(2)} KB

                            </div>

                        </div>

                    </div>

                </div>
            `;
        }

        chatBody.scrollTop =
        chatBody.scrollHeight;

    }catch(error){
        uploadingDiv.remove();

        console.log(
            "Upload Error:",
            error
        );
    }
});

/* =========================
   VOICE INPUT
========================= */

function startVoice(){

    const recognition =
    new webkitSpeechRecognition();

    recognition.lang = "en-US";

    recognition.start();

    recognition.onresult =
    function(event){

        document
        .getElementById("message")
        .value =
        event.results[0][0].transcript;
    }
}

/* =========================
   CLOSE MENU OUTSIDE CLICK
========================= */

document.addEventListener(
"click",
function(event){

    const wrapper =
    document.querySelector(
        ".attachment-wrapper"
    );

    const menu =
    document.getElementById(
        "attachmentMenu"
    );

    if(
        !wrapper.contains(event.target)
    ){

        menu.style.display = "none";
    }
});

/* =========================
   AUDIO TOGGLE
========================= */

let isSpeaking = false;

function toggleSpeech(button, text){

    // =========================
    // STOP SPEECH
    // =========================

    if(isSpeaking){

        window.speechSynthesis.cancel();

        isSpeaking = false;

        button.innerHTML = "🔇";

        return;
    }

    // =========================
    // START SPEECH
    // =========================

    const speech =
    new SpeechSynthesisUtterance(
        text
    );

    speech.lang = "en-US";

    speech.rate = 1;

    speech.pitch = 1;

    speech.volume = 1;

    window.speechSynthesis.speak(
        speech
    );

    isSpeaking = true;

    button.innerHTML = "🔊";

    // =========================
    // RESET AFTER FINISH
    // =========================

    speech.onend = function(){

        isSpeaking = false;

        button.innerHTML = "🔇";
    };
}
