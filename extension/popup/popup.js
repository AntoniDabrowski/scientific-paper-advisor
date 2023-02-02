window.onload = function() {
    chrome.storage.local.get(["HOST_IP"]).then((result) => {
        const myIP = document.getElementById("myIP");
        if (result) {
            myIP.value = result["HOST_IP"];
        }
        else {
            chrome.storage.local.set({ 'HOST_IP': "34.118.92.99"});
            myIP.value = "34.118.92.99";
        }

        if (myIP.value === "34.118.92.99") {
            const server_button = document.getElementById("server_button");
            server_button.checked = true;
        }
        else if (myIP.value === "127.0.0.1") {
            const local_button = document.getElementById("local_button");
            local_button.checked = true;
        }
        else {
            const custom_button = document.getElementById("custom_button");
            custom_button.checked = true;
        }
    });
};

function checkIfValidIP(str) {
    const regexExp = /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/gi;
    return regexExp.test(str);
}

const btn = document.getElementById("btn");
btn.addEventListener('click', function(){
    var host = document.getElementById("myIP").value;
    if (checkIfValidIP(host)) {
        chrome.storage.local.set({ 'HOST_IP': host });
        alert("Host IP set to: "+ host);
    }
    else {
        alert(host + " is not valid IP adress");
    }
});

const server_button = document.getElementById("server_button");
server_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    myIP.value = server_button.value;
});


const local_button = document.getElementById("local_button");
local_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    myIP.value = local_button.value;
});

const custom_button = document.getElementById("custom_button");
custom_button.addEventListener('click', function(){
    const myIP = document.getElementById("myIP");
    if (myIP.value == "34.118.92.99" || myIP.value == "127.0.0.1") {
        myIP.value = custom_button.value;
    }
});