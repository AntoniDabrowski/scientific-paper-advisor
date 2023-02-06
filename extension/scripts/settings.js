export let PROTOCOL = 'https://'
export let IP = '34.118.92.99'
export let BACKEND_SERVER_URL = `${PROTOCOL}${IP}:8000`;

export let FURTHER_RESEARCH_ENDPOINT = `${BACKEND_SERVER_URL}/frquestions/pdfparser`;
export let ARTICLE_GRAPH_ENDPOINT = `${BACKEND_SERVER_URL}/articlegraph`;
export let ARTICLE_GRAPH_LEFT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandleft`;
export let ARTICLE_GRAPH_RIGHT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandright`;

function update_endpoints(PROTOCOL, IP){
    BACKEND_SERVER_URL = PROTOCOL + IP + ':8000';
    FURTHER_RESEARCH_ENDPOINT = `${BACKEND_SERVER_URL}/frquestions/pdfparser`;
    ARTICLE_GRAPH_ENDPOINT = `${BACKEND_SERVER_URL}/articlegraph`;
    ARTICLE_GRAPH_LEFT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandleft`;
    ARTICLE_GRAPH_RIGHT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandright`;
}

window.onload = function() {
    chrome.storage.local.get(["HOST_IP"]).then((result) => {
        if (Object.keys(result).length === 0) {
            IP = "34.118.92.99";
            chrome.storage.local.set({ 'HOST_IP': "34.118.92.99"});
            update_endpoints(PROTOCOL, IP);
        }
        else {
            IP = result["HOST_IP"];
            update_endpoints(PROTOCOL, IP);
        }
    });

    chrome.storage.local.get(["PROTOCOL"]).then((result) => {
        if (Object.keys(result).length === 0) {
            PROTOCOL = "https://";
            chrome.storage.local.set({ 'PROTOCOL': "https://"});
            update_endpoints(PROTOCOL, IP);
        }
        else {
            PROTOCOL = result["PROTOCOL"];
            update_endpoints(PROTOCOL, IP);

        }
    });
};

chrome.storage.onChanged.addListener((changes, namespace) => {
    for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
        if (key === "PROTOCOL") {
            PROTOCOL = newValue;
        }
        else if (key === "HOST_IP") {
            IP = newValue;
        }
    }
    update_endpoints(PROTOCOL, IP);
});