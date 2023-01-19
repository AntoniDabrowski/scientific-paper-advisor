const {create_graph_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data} = require("./utils");
const {get_graph_layout} = require("./backend_communication");
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

function draw_scatter_plot(drawing_board, i, x) {
    console.log("In draw_scatter_plot");
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

function handle_menu(menu, drawing_board, i, x) {
    console.log("In handle_menu");
    x.classList.toggle("active");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    }
    else {
        menu.style.display = "block";
    }

    draw_graph_of_connections(drawing_board, i, x);
}

if (pdf_results) {
    var _loop = function _loop(i) {
        var create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = 'project button';

        var drawing_board = document.createElement("div");
        drawing_board.className = "content";
        drawing_board.id = "graph_" + i;
        drawing_board.style.display = "none";

        var menu = document.createElement("div");
        menu.className = "menu";
        menu.id = "menu_" + i;
        menu.style.display = "none";

        var connection_graph = document.createElement("button");
        connection_graph.innerHTML = "Connection graph";
        connection_graph.onclick = function () {
            draw_graph_of_connections(drawing_board, i, this);
        };
        menu.appendChild(connection_graph);


        var scatter_plot = document.createElement("button");
        scatter_plot.innerHTML = "Scatter plot";
        scatter_plot.onclick = function () {
            draw_graph_of_connections(drawing_board, i, this);
            alert("Add scatter plot");
        };
        menu.appendChild(scatter_plot);

        create_graph.addEventListener("click", function () {
            handle_menu(menu, drawing_board, i, this);
        });

        var links_of_result = void 0;
        var search_result_box = void 0;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', drawing_board);
        links_of_result[1].insertAdjacentElement('afterend', menu);
    };

    for (var i = 0; i < pdf_results.length; i++) {
        _loop(i);
    }
}