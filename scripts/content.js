/*
class ArticleNode {
    constructor(name) {
        this.name = name;
        this.favoriteFlavors = [];
    }

    addArticle(flavor) {
        this.favoriteFlavors.push(flavor);
    }
}
*/
var Plotly = require('plotly.js-strict-dist')

const pdf_results = document.getElementsByClassName("gs_ggs gs_fl")


if (pdf_results) {
    for (let i = 0; i < pdf_results.length; i++) {
        const create_graph = document.createElement("button");
        create_graph.className = "collapsible";
        create_graph.textContent = `project button`;

        const drawing_board = document.createElement("div");
        //drawing_board.innerHTML = "<p>Lorem ipsum...</p>";
        drawing_board.className = "content";
        drawing_board.id = "graph"
        drawing_board.style.display = "none"

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

        Plotly.newPlot('graph', [{
            x: [1, 2, 3],
            y: [2, 1, 3]
        }], {
            sliders: [{
                pad: {t: 30},
                currentvalue: {
                    xanchor: 'right',
                    prefix: 'color: ',
                    font: {
                        color: '#888',
                        size: 20
                    }
                },
                steps: [{
                    label: 'red',
                    method: 'restyle',
                    args: ['line.color', 'red']
                }, {
                    label: 'green',
                    method: 'restyle',
                    args: ['line.color', 'green']
                }, {
                    label: 'blue',
                    method: 'restyle',
                    args: ['line.color', 'blue']
                }]
            }]
        });

    }

}