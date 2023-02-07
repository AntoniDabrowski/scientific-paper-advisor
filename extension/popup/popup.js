window.onload = function() {
    chrome.storage.local.get(["HOST_IP"]).then((result_IP) => {
        const myIP = document.getElementById("myIP");
        if (Object.keys(result_IP).length === 0) {
            chrome.storage.local.set({ 'HOST_IP': "backend.spaserver.dev"});
            myIP.value = "backend.spaserver.dev";
        }
        else {
            myIP.value = result_IP["HOST_IP"];
        }

        if (myIP.value == "backend.spaserver.dev") {
            const server_button = document.getElementById("server_button");
            server_button.checked = true;
        }
        else if (myIP.value == "127.0.0.1") {
            const local_button = document.getElementById("local_button");
            local_button.checked = true;
        }
        else {
            const custom_button = document.getElementById("custom_button");
            custom_button.checked = true;
        }

        chrome.storage.local.get(["PROTOCOL"]).then((result) => {
            const http_protocol = document.getElementById("http");
            const https_protocol = document.getElementById("https");
            if (Object.keys(result).length === 0) {
                const local_button = document.getElementById("local_button");
                const server_button = document.getElementById("server_button");
                if (local_button.checked) {
                    chrome.storage.local.set({ 'PROTOCOL': 'http://' });
                    http_protocol.checked = true;
                }
                else if (server_button.checked) {
                    chrome.storage.local.set({ 'PROTOCOL': 'https://' });
                    https_protocol.checked = true;
                }
                else {
                    chrome.storage.local.set({ 'PROTOCOL': 'https://' });
                    https_protocol.checked = true;
                }
            }
            else {
                if (result['PROTOCOL'] === http_protocol.value) {
                    http_protocol.checked = true;
                }
                else {
                    https_protocol.checked = true;
                }
            }
        });
    });
};

const btn = document.getElementById("btn");
btn.addEventListener('click', function(){
    var host = document.getElementById("myIP").value;
    const http_protocol = document.getElementById("http");
    const https_protocol = document.getElementById("https");
    let current_protocol;
    if (http_protocol.checked) {
        current_protocol = http_protocol.value;
        chrome.storage.local.set({ 'PROTOCOL': http_protocol.value });
    }
    else {
        current_protocol = https_protocol.value;
        chrome.storage.local.set({ 'PROTOCOL': https_protocol.value });
    }

    chrome.storage.local.set({ 'HOST_IP': host });
    alert("Host IP set to: "+ host + "\nWith protocol: " + current_protocol);
});


const http_protocol = document.getElementById("http");
const https_protocol = document.getElementById("https");

const server_button = document.getElementById("server_button");
server_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    myIP.value = server_button.value;
    https_protocol.checked = true;
});


const local_button = document.getElementById("local_button");
local_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    myIP.value = local_button.value;
    http_protocol.checked = true;
});

const custom_button = document.getElementById("custom_button");
custom_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    if (myIP.value == "backend.spaserver.dev" || myIP.value == "127.0.0.1") {
        myIP.value = custom_button.value;
    }
});