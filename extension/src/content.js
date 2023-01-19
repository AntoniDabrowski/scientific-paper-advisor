const {create_graph_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data} = require("./utils");
const {get_graph_layout} = require("./backend_communication");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")

function rest(drawing_board, i, x) {
    x.classList.toggle("active");
    if (drawing_board.style.display === "block") {
        drawing_board.style.display = "none";
        purge_graph(drawing_board.id)
    } else {
        drawing_board.style.display = "block";
        let article_data = extract_article_data(pdf_results[i].parentNode)
        let graph_schema = get_graph_layout(article_data)
        // TODO add waiting animation
        graph_schema.then(returned_json => {
            create_graph_on_scholar_result(drawing_board.id, returned_json);
        }).catch(error => {
            // TODO add action in case of failure.
            console.error(error)
        })
    }
}


if (pdf_results) {
    for (let i = 0; i < pdf_results.length; i++) {
        let divid = "graph_" + i
        const create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = 'project button';

        const drawing_board = document.createElement("div");
        drawing_board.className = "content";
        drawing_board.id = divid;
        drawing_board.style.display = "none";

        create_graph.addEventListener("click", function () {
            rest(drawing_board, i, this);
            });

        let links_of_result;
        let search_result_box;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', drawing_board)
    }
}