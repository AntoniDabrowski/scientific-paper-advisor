export const BACKEND_SERVER_URL='http://127.0.0.1:8000'
export const FURTHER_RESEARCH_ENDPOINT=`${BACKEND_SERVER_URL}/frquestions/pdfparser`
export const ARTICLE_GRAPH_ENDPOINT=`${BACKEND_SERVER_URL}/articlegraph`
export const ARTICLE_GRAPH_LEFT_EXPAND=`${ARTICLE_GRAPH_ENDPOINT}/expandleft`
export const ARTICLE_GRAPH_RIGHT_EXPAND=`${ARTICLE_GRAPH_ENDPOINT}/expandright`

//function get_adress(){
//    let IP;
//    chrome.runtime.sendMessage('get-IP', (response) => {
//        console.log('received user data', response);
//        IP = response;
//    });
//    console.log('IP:', IP);
//};