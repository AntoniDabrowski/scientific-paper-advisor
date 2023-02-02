const {create_graph_on_scholar_result, create_scatter_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data, extract_pdf_url, show_loader, hide_loader} = require("./utils");
const {get_graph_layout, get_scatter_layout, update_schema_left, update_schema_right} = require("./backend_communication");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")
let json_storage = [];

function draw_graph_of_connections(graph_menu, i, x) {
    x.classList.toggle("active");
    let graph = graph_menu.children[0]
    let buttons_menu = graph_menu.children[1]

    if (graph_menu.style.display === "block") {
        graph_menu.style.display = "none";
        purge_graph(graph.id);
    } else {
        graph_menu.style.display = "block";
        if (json_storage[i] === "NO RECORD") {
            let article_data = extract_article_data(pdf_results[i].parentNode);
            let graph_schema = get_graph_layout(article_data);
            buttons_menu.style.display = "none";
            show_loader(graph.id);

            graph_schema.then(function (returned_json) {
                hide_loader(graph.id);
                json_storage[i] = returned_json
                create_graph_on_scholar_result(graph.id, returned_json);
                buttons_menu.style.display = "block";
            }).catch(function (error) {
                // TODO add action in case of failure.
                buttons_menu.style.display = "none";
                hide_loader(graph.id);
                console.error(error);
            });
        } else {
            create_graph_on_scholar_result(graph.id, json_storage[i]);
        }

    }
}

function draw_scatter_plot(scatter_menu, i, x, scatter_data, not_internal=true) {
    x.classList.toggle("active");

    let scatter = scatter_menu.children[0]
    let buttons_menu = scatter_menu.children[1]

    if (scatter_menu.style.display === "block" && not_internal) {
        scatter_menu.style.display = "none";
        purge_graph(scatter.id);
    } else {
        scatter_menu.style.display = "block";
        var article_data = extract_pdf_url(pdf_results[i]);
        var graph_schema = get_scatter_layout(article_data);
        show_loader(scatter.id)

        graph_schema.then(function (returned_json) {
            hide_loader(scatter.id);
            scatter.style.display = "block";
            create_scatter_on_scholar_result(scatter, returned_json, scatter_data);
            buttons_menu.style.display = "block";
        }).catch(function (error) {
            scatter_menu.style.display = "none";
            hide_loader(scatter.id);
            console.error(error);
        });
    }
}


function handle_menu(menu, graph_menu, scatter_menu, i, x, scatter_data) {
    x.classList.toggle("active");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }

    if (graph_menu.style.display === "none" && scatter_menu.style.display === "none") {
        draw_scatter_plot(scatter_menu, i, x, scatter_data);
    } else if (scatter_menu.style.display === "block") {
        draw_scatter_plot(scatter_menu, i, x, scatter_data);
    } else {
        draw_graph_of_connections(graph_menu, i, x);
    }

}

function expand_graph_left(graph_menu, i) {
    if (json_storage[i] !== "NO RECORD") {
        let graph = graph_menu.children[0]
        let schema_promise = update_schema_left(json_storage[i])

        schema_promise.then(function (returned_json) {
            json_storage[i] = returned_json
            create_graph_on_scholar_result(graph.id, returned_json);
        }).catch(function (error) {
            // TODO add action in case of failure.
            console.error(error);
        });

    }
}

function expand_graph_right(graph_menu, i) {
    if (json_storage[i] !== "NO RECORD") {
        let graph = graph_menu.children[0]

        let schema_promise = update_schema_right(json_storage[i])

        schema_promise.then(function (returned_json) {
            json_storage[i] = returned_json
            create_graph_on_scholar_result(graph.id, returned_json);
        }).catch(function (error) {
            // TODO add action in case of failure.
            console.error(error);
        });

    }
}

if (pdf_results) {
    var _loop = function _loop(i) {
        var create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.classList.add("projectbutton")
        create_graph.textContent = 'SPA';
        create_graph.title = "Scientific Papers Advisor - puts the search result in the context " +
            "of its references and uses in the later works."

        // Graph display
        var graph_menu = document.createElement("div");
        graph_menu.className = "content";
        graph_menu.id = "graph_menu_" + i;
        graph_menu.style.display = "none";

        var graph_buttons = document.createElement("div");
        graph_buttons.id = "graph_buttons_" + i;

        var graph = document.createElement("div");
        graph.id = "graph_" + i;

        var left_button = document.createElement("button");
        left_button.textContent = 'Expand left side';
        left_button.className = 'projectbutton'
        left_button.classList.add('doublebutton')
        left_button.id = "left_button_" + i;
        left_button.title = "This option adds new column at the left side of the graph." +
            "Articles in that column are the representatives of publications referenced in the previous left most column."
        graph_buttons.appendChild(left_button)

        var right_button = document.createElement("button");
        right_button.textContent = 'Expand right side';
        right_button.className = 'projectbutton'
        right_button.classList.add('doublebutton')
        right_button.id = "right_button_" + i;
        right_button.title = "This option adds next generation to the graph," +
            "articles citing the publications from the current right most column."
        graph_buttons.appendChild(right_button)

        graph_menu.appendChild(graph);
        graph_menu.appendChild(graph_buttons);


        // Scatter display
        let scatter_data = 'further_research';

        var scatter_menu = document.createElement("div");
        scatter_menu.className = "content";
        scatter_menu.id = "scatter_menu_" + i;
        scatter_menu.style.display = "none";

        var scatter_buttons = document.createElement("div");
        scatter_buttons.id = "scatter_buttons_" + i;

        var scatter = document.createElement("div");
        scatter.id = "scatter_" + i;
        scatter.style.display = "none";

        var left_button_scatter = document.createElement("button");
        left_button_scatter.textContent = 'Further research';
        left_button_scatter.className = 'projectbutton';
        left_button_scatter.classList.add('doublebutton');
        left_button_scatter.id = "left_button_scatter_" + i;
        left_button_scatter.title="Shows suggestions for additional study contained " +
            "in the recent articles from the same category as the search result." +
            "Splitted into clusters based on similarity. Each cluster has a representative deemed most relevant."
        scatter_buttons.appendChild(left_button_scatter);

        var right_button_scatter = document.createElement("button");
        right_button_scatter.textContent = 'Abstract';
        right_button_scatter.className = 'projectbutton';
        right_button_scatter.classList.add('doublebutton');
        right_button_scatter.id = "right_button_scatter_" + i;
        right_button_scatter.title = "Shows abstracts of the recent articles " +
            "from the same category as the search result." +
            "Splitted into clusters based on similarity. Each cluster has a representative deemed most relevant."
        scatter_buttons.appendChild(right_button_scatter);

        scatter_menu.appendChild(scatter);
        scatter_menu.appendChild(scatter_buttons);

        // Menu container and buttons
        var menu = document.createElement("div");
        menu.className = "menu";
        menu.id = "menu_" + i;
        menu.style.display = "none";

        var scatter_plot = document.createElement("button");
        scatter_plot.textContent = "Scatter plot";
        scatter_plot.className = 'projectbutton';
        scatter_plot.classList.add('doublebutton');
        scatter_plot.onclick = function () {
            if (scatter_menu.style.display === "none") {
                graph_menu.style.display = "none"
                draw_scatter_plot(scatter_menu, i, this, scatter_data);
            }
        };
        scatter_plot.title="Switch to the graph showing interesting data about " +
            "the scientific category your search result belongs to."
        menu.appendChild(scatter_plot);

        json_storage[i] = "NO RECORD"

        var connection_graph = document.createElement("button");
        connection_graph.textContent = "Connection graph";
        connection_graph.className = 'projectbutton';
        connection_graph.classList.add('doublebutton')
        connection_graph.onclick = function () {
            if (graph_menu.style.display === "none") {
                scatter_menu.style.display = "none"
                draw_graph_of_connections(graph_menu, i, this);
            }
        };
        connection_graph.title="Switch to the graph showing citation context of your search result."
        menu.appendChild(connection_graph);


        create_graph.addEventListener("click", function () {
            handle_menu(menu, graph_menu, scatter_menu, i, this, scatter_data);
        });

        left_button.addEventListener("click", function () {
            expand_graph_left(graph_menu, i);
        });

        right_button.addEventListener("click", function () {
            expand_graph_right(graph_menu, i);
        });

        left_button_scatter.addEventListener("click", function () {
            scatter_data = 'further_research';
            draw_scatter_plot(scatter_menu, i, this, scatter_data, not_internal=false);
        });

        right_button_scatter.addEventListener("click", function () {
            scatter_data = 'abstract';
            draw_scatter_plot(scatter_menu, i, this, scatter_data, not_internal=false);
        });

        let links_of_result;
        let search_result_box;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', graph_menu);
        links_of_result[1].insertAdjacentElement('afterend', scatter_menu);
        links_of_result[1].insertAdjacentElement('afterend', menu);
    };

    for (var i = 0; i < pdf_results.length; i++) {
        _loop(i);
    }
}