const {create_graph_on_scholar_result, purge_graph} = require("./graphs");
const {extract_article_data} = require("./utils");
const {get_graph_layout} = require("./backend_communication");

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
                purge_graph(divid)
            } else {
                drawing_board.style.display = "block";
                let article_data = extract_article_data(pdf_results[i].parentNode)
                let graph_schema = get_graph_layout(article_data)
                console.log('Just before graph schema')
                graph_schema.then(returned_json => {
                    console.log('Inside then')
                    create_graph_on_scholar_result(divid, returned_json.body);
                }).catch(error => {
                    console.error("inside catch")
                    const json_str = '{"directed": false, "multigraph": false, "graph": {}, "nodes": [{"title": "Genetic algorithm: Review and application", "authors": ["D Gupta", "D Husain", "M Kumar", "N Upreti"], "num_publications": 471, "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3529843", "subset": 0, "id": 0}, {"title": "Evaluation on state of charge estimation of batteries with adaptive extended Kalman filter by experiment approach", "authors": ["R Xiong", "H He", "F Sun", "K Zhao"], "num_publications": 399, "url": "https://ieeexplore.ieee.org/abstract/document/6323045/", "subset": 1, "id": 1}, {"title": "Application of artificial neural networks for catalysis: a review", "authors": ["H Li", "Z Zhang", "Z Liu"], "num_publications": 203, "url": "https://www.mdpi.com/230962", "subset": 1, "id": 2}, {"title": "Learning path personalization and recommendation methods: A survey of the state-of-the-art", "authors": ["AH Nabizadeh", "JP Leal", "HN Rafsanjani"], "num_publications": 73, "url": "https://www.sciencedirect.com/science/article/pii/S0957417420304206", "subset": 1, "id": 3}, {"title": "Prediction of maximum pitting corrosion depth in oil and gas pipelines", "authors": ["MEAB Seghier", "B Keshtegar", "KF Tee", "T Zayed"], "num_publications": 71, "url": "https://www.sciencedirect.com/science/article/pii/S1350630719318746", "subset": 1, "id": 4}, {"title": "Modeling, diagnostics, optimization, and control of internal combustion engines via modern machine learning techniques: A review and future directions", "authors": ["M Aliramezani", "CR Koch", "M Shahbakhti"], "num_publications": 30, "url": "https://www.sciencedirect.com/science/article/pii/S0360128521000654", "subset": 1, "id": 5}], "links": [{"source": 0, "target": 1}, {"source": 0, "target": 2}, {"source": 0, "target": 3}, {"source": 0, "target": 4}, {"source": 0, "target": 5}], "layout": {"0": [-0.41666666666666663, 0.0], "5": [0.08333333333333334, -1.0], "4": [0.08333333333333334, -0.5], "3": [0.08333333333333334, 0.0], "2": [0.08333333333333334, 0.5], "1": [0.08333333333333334, 1.0]}}'
                    create_graph_on_scholar_result(divid, json_str);
                })
            }
        });

        let links_of_result;
        let search_result_box;


        pdf_results[i].insertAdjacentElement("beforeend", create_graph);
        search_result_box = pdf_results[i].parentNode;
        links_of_result = search_result_box.getElementsByClassName('gs_fl');
        links_of_result[1].insertAdjacentElement('afterend', drawing_board)
    }

}