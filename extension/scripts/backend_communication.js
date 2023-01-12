import {get} from "./utils";
import {ARTICLE_GRAPH_ENDPOINT} from "./settings";

export function get_graph_layout(article_data) {
    const params = {
        authors: article_data.authors,
        title: article_data.title
    };

    const response = get(ARTICLE_GRAPH_ENDPOINT, params)
    console.log(response)

    return 1;
}