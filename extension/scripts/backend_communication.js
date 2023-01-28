import {get} from "./utils";
import {ARTICLE_GRAPH_ENDPOINT} from "./settings";
import {FURTHER_RESEARCH_ENDPOINT} from "./settings";

export async function get_graph_layout(article_data) {
    const params = {
        authors: article_data.authors,
        title: article_data.title
    };

    return get(ARTICLE_GRAPH_ENDPOINT, params);
}


export async function get_scatter_layout(article_data) {
    const params = {
        pdfurl: article_data.url,
    };

    return get(FURTHER_RESEARCH_ENDPOINT, params);
}