import {get, post} from "./utils";
import {
    ARTICLE_GRAPH_ENDPOINT,
    ARTICLE_GRAPH_LEFT_EXPAND,
    ARTICLE_GRAPH_RIGHT_EXPAND,
    FURTHER_RESEARCH_ENDPOINT
} from "./settings";

export async function get_graph_layout(article_data) {
    const params = {
        authors: article_data.authors,
        title: article_data.title,
        pdfurl: article_data.url
    };

    return get(ARTICLE_GRAPH_ENDPOINT, params);
}

export async function update_schema_left(graph_data) {
    return fetch(ARTICLE_GRAPH_LEFT_EXPAND, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(graph_data)
    }).then(response => response.json())

}


export async function update_schema_right(graph_data) {
    return fetch(ARTICLE_GRAPH_RIGHT_EXPAND, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(graph_data)
    }).then(response => response.json())
}


export async function get_scatter_layout(article_data) {
    const params = {
        pdfurl: article_data.url,
    };

    return get(FURTHER_RESEARCH_ENDPOINT, params);
}