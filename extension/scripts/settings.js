export let BACKEND_SERVER_URL = 'http://34.118.92.99:8000';

export let FURTHER_RESEARCH_ENDPOINT = `${BACKEND_SERVER_URL}/frquestions/pdfparser`;
export let ARTICLE_GRAPH_ENDPOINT = `${BACKEND_SERVER_URL}/articlegraph`;
export let ARTICLE_GRAPH_LEFT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandleft`;
export let ARTICLE_GRAPH_RIGHT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandright`;

function update_endpoints(IP){
    BACKEND_SERVER_URL = 'http://' + IP + ':8000';
    FURTHER_RESEARCH_ENDPOINT = `${BACKEND_SERVER_URL}/frquestions/pdfparser`;
    ARTICLE_GRAPH_ENDPOINT = `${BACKEND_SERVER_URL}/articlegraph`;
    ARTICLE_GRAPH_LEFT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandleft`;
    ARTICLE_GRAPH_RIGHT_EXPAND = `${ARTICLE_GRAPH_ENDPOINT}/expandright`;
}

window.onload = function() {
    chrome.storage.local.get(["HOST_IP"]).then((result) => {
        const myIP = document.getElementById("myIP");
        if (result) {
            update_endpoints(result["HOST_IP"])
        }
        else {
            chrome.storage.local.set({ 'HOST_IP': "34.118.92.99"});
            update_endpoints('34.118.92.99');
        }
    });
};

chrome.storage.onChanged.addListener((changes, namespace) => {
    for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
        update_endpoints(newValue);
    }
});