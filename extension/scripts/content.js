const {create_graph_on_scholar_result, create_scatter_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data, extract_pdf_url, show_loader, hide_loader, DefaultDict} = require("./utils");
const {get_graph_layout, get_scatter_layout} = require("./backend_communication");
const {menu} = require("./menu");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")
let json_storage = [];

function draw_graph_of_connections(graph, i, x) {
    console.log("In draw_graph_of_connections");
    x.classList.toggle("active");
    if (graph.style.display === "block") {
        graph.style.display = "none";
        purge_graph(graph.id);
    } else {
        graph.style.display = "block";
        if (json_storage[i] === "NO RECORD")
        {
            let article_data = extract_article_data(pdf_results[i].parentNode);
            let graph_schema = get_graph_layout(article_data);
            show_loader(graph.id);
            graph_schema.then(function (returned_json) {
                hide_loader(graph.id);
                json_storage[i] = returned_json
                create_graph_on_scholar_result(graph.id, returned_json);
            }).catch(function (error) {
                // TODO add action in case of failure.
                hide_loader(graph.id);
                console.error(error);
            });
        } else {
            create_graph_on_scholar_result(graph.id, json_storage[i]);
        }

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
        show_loader(scatter.id);
        graph_schema.then(function (returned_json) {
            hide_loader(scatter.id);
            create_scatter_on_scholar_result(scatter, returned_json);
        }).catch(function (error) {
            // TODO add action in case of failure.
            hide_loader(scatter.id);
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
        draw_scatter_plot(scatter, i, x);
    } else if (scatter.style.display === "block") {
        draw_scatter_plot(scatter, i, x);
    } else {
        draw_graph_of_connections(graph, i, x);
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

        json_storage[i] = "NO RECORD"

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

        let links_of_result;
        let search_result_box;


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