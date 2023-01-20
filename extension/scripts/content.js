const {create_graph_on_scholar_result, create_scatter_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data, extract_pdf_url} = require("./utils");
const {get_graph_layout, get_scatter_layout} = require("./backend_communication");
const {menu} = require("./menu");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")

function draw_graph_of_connections(drawing_board, i, x) {
    console.log("In draw_graph_of_connections");
    x.classList.toggle("active");
    if (drawing_board.style.display === "block") {
        drawing_board.style.display = "none";
        purge_graph(drawing_board.id);
    } else {
        drawing_board.style.display = "block";
        var article_data = extract_article_data(pdf_results[i].parentNode);
        var graph_schema = get_graph_layout(article_data);
        // TODO add waiting animation
        graph_schema.then(function (returned_json) {
            create_graph_on_scholar_result(drawing_board.id, returned_json);
        }).catch(function (error) {
            // TODO add action in case of failure.
            console.error(error);
        });
    }
}

function draw_scatter_plot(scatter, i, x) {
    console.log("In draw_scatter_plot");
    x.classList.toggle("active");
    if (scatter.style.display === "block") {
        scatter.style.display = "none";
        purge_graph(scatter.id);
    } else {
        scatter.style.display = "block";
        var article_data = extract_pdf_url(pdf_results[i]);
        console.log("article_data: ",article_data);
        var graph_schema = get_scatter_layout(article_data)
        console.log("graph_schema: ",graph_schema);
        // TODO add waiting animation
        graph_schema.then(function (returned_json) {
            create_scatter_on_scholar_result(scatter, returned_json);
        }).catch(function (error) {
            // TODO add action in case of failure.
            console.error(error);
        });
    }
}

function handle_menu(menu, graph, scatter, i, x) {
    console.log("In handle_menu");
    x.classList.toggle("active");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    }
    else {
        menu.style.display = "block";
    }

    if (graph.style.display === "none" && scatter.style.display === "none") {
        draw_graph_of_connections(graph, i, x);
    } else if (graph.style.display === "block") {
        draw_graph_of_connections(graph, i, x);
    } else {
        draw_scatter_plot(scatter, i, x);
    }

}

if (pdf_results) {
    var _loop = function _loop(i) {
        var create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = 'project button';

        // Drawing boards
        var graph = document.createElement("div");
        graph.className = "content";
        graph.id = "graph_" + i;
        graph.style.display = "none";

        var scatter = document.createElement("div");
        scatter.className = "content";
        scatter.id = "scatter_" + i;
        scatter.style.display = "none";

        // Menu container and buttons
        var menu = document.createElement("div");
        menu.className = "menu";
        menu.id = "menu_" + i;
        menu.style.display = "none";

        var connection_graph = document.createElement("button");
        connection_graph.innerHTML = "Connection graph";
        connection_graph.onclick = function () {
            if (graph.style.display === "none") {
                draw_scatter_plot(scatter, i, this);
                draw_graph_of_connections(graph, i, this);
            }
        };
        menu.appendChild(connection_graph);


        var scatter_plot = document.createElement("button");
        scatter_plot.innerHTML = "Scatter plot";
        scatter_plot.onclick = function () {
            if (scatter.style.display === "none") {
                draw_graph_of_connections(graph, i, this);
                draw_scatter_plot(scatter, i, this);
            }
        };
        menu.appendChild(scatter_plot);

        create_graph.addEventListener("click", function () {
            handle_menu(menu, graph, scatter, i, this);
        });

        var links_of_result = void 0;
        var search_result_box = void 0;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', graph);
        links_of_result[1].insertAdjacentElement('afterend', scatter);
        links_of_result[1].insertAdjacentElement('afterend', menu);
    };

    for (var i = 0; i < pdf_results.length; i++) {
        _loop(i);
    }
}