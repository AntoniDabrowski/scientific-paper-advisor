const {create_graph_on_scholar_result} = require("./graphs");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")


if (pdf_results) {
    for (let i = 0; i < pdf_results.length; i++) {
        let divid = "graph_" + i
        const create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = `project button`;

        const drawing_board = document.createElement("div");
        drawing_board.className = "content";
        drawing_board.id = divid;
        drawing_board.style.display = "none";

        create_graph.addEventListener("click", function () {
            this.classList.toggle("active");
            if (drawing_board.style.display === "block") {
                drawing_board.style.display = "none";
            } else {
                drawing_board.style.display = "block";
            }
        });

        let links_of_result;
        let search_result_box;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', drawing_board)

        create_graph_on_scholar_result(divid, [1, 2, 3], [2, 1, 3])

    }

}