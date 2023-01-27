const {create_graph_on_scholar_result, create_scatter_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data, extract_pdf_url, show_loader, hide_loader} = require("./utils");
const {get_graph_layout, get_scatter_layout, update_schema_left, update_schema_right} = require("./backend_communication");

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")
let json_storage = [];

function draw_graph_of_connections(graph_menu, i, x) {
    console.log("In draw_graph_of_connections");
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

function draw_scatter_plot(scatter, i, x) {
    console.log("In draw_scatter_plot");
    x.classList.toggle("active");
    if (scatter.style.display === "block") {
        scatter.style.display = "none";
        purge_graph(scatter.id);
    } else {
        scatter.style.display = "block";
        var article_data = extract_pdf_url(pdf_results[i]);
        console.log("article_data: ", article_data);
        var graph_schema = get_scatter_layout(article_data)
        console.log("graph_schema: ", graph_schema);
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

function handle_menu(menu, graph_menu, scatter, i, x) {
    console.log("In handle_menu");
    x.classList.toggle("active");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }

    if (graph_menu.style.display === "none" && scatter.style.display === "none") {
        draw_scatter_plot(scatter, i, x);
    } else if (scatter.style.display === "block") {
        draw_scatter_plot(scatter, i, x);
    } else {
        draw_graph_of_connections(graph_menu, i, x);
    }

}

function expand_graph_left(graph_menu, i) {
    if (json_storage[i] !== "NO RECORD") {
        let graph = graph_menu.children[0]
        //let buttons_menu = graph_menu.children[1]

        let schema_promise = update_schema_left(json_storage[i])

        schema_promise.then(function (returned_json) {
            //hide_loader(graph.id);
            json_storage[i] = returned_json
            create_graph_on_scholar_result(graph.id, returned_json);
            //buttons_menu.style.display = "block";
        }).catch(function (error) {
            // TODO add action in case of failure.
            //buttons_menu.style.display = "none";
            //hide_loader(graph.id);
            console.error(error);
        });

    }
}

function expand_graph_right(graph_menu, i) {
    if (json_storage[i] !== "NO RECORD") {
        let graph = graph_menu.children[0]
        //let buttons_menu = graph_menu.children[1]

        let schema_promise = update_schema_right(json_storage[i])

        schema_promise.then(function (returned_json) {
            //hide_loader(graph.id);
            json_storage[i] = returned_json
            create_graph_on_scholar_result(graph.id, returned_json);
            //buttons_menu.style.display = "block";
        }).catch(function (error) {
            // TODO add action in case of failure.
            //buttons_menu.style.display = "none";
            //hide_loader(graph.id);
            console.error(error);
        });

    }
}

if (pdf_results) {
    var _loop = function _loop(i) {
        var create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = 'project button';

        var graph_menu = document.createElement("div");
        graph_menu.className = "content";
        graph_menu.id = "graph_menu_" + i;
        graph_menu.style.display = "none";

        var graph_buttons = document.createElement("div");
        graph_buttons.id = "graph_buttons_" + i;

        var graph = document.createElement("div");
        graph.id = "graph_" + i;

        var left_button = document.createElement("button");
        left_button.textContent = 'left button';
        left_button.className = 'btn'
        left_button.id = "left_button_" + i;
        graph_buttons.appendChild(left_button)

        var right_button = document.createElement("button");
        right_button.textContent = 'right button';
        right_button.className = 'btn'
        right_button.id = "right_button_" + i;
        graph_buttons.appendChild(right_button)

        graph_menu.appendChild(graph)
        graph_menu.appendChild(graph_buttons)

        var scatter = document.createElement("div");
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
        connection_graph.className = 'btn';
        connection_graph.onclick = function () {
            console.debug(graph_menu)
            if (graph_menu.style.display === "none") {
                scatter.style.display = "none"
                draw_graph_of_connections(graph_menu, i, this);
            }
        };
        menu.appendChild(connection_graph);


        var scatter_plot = document.createElement("button");
        scatter_plot.innerHTML = "Scatter plot";
        scatter_plot.className = 'btn';
        scatter_plot.onclick = function () {
            if (scatter.style.display === "none") {
                graph_menu.style.display = "none"
                draw_scatter_plot(scatter, i, this);
            }
        };
        menu.appendChild(scatter_plot);

        create_graph.addEventListener("click", function () {
            handle_menu(menu, graph_menu, scatter, i, this);
        });

        left_button.addEventListener("click", function () {
            expand_graph_left(graph_menu, i);
        });

        right_button.addEventListener("click", function () {
            expand_graph_right(graph_menu, i);
        });

        let links_of_result;
        let search_result_box;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', graph_menu);
        links_of_result[1].insertAdjacentElement('afterend', scatter);
        links_of_result[1].insertAdjacentElement('afterend', menu);
    };

    for (var i = 0; i < pdf_results.length; i++) {
        _loop(i);
    }
}