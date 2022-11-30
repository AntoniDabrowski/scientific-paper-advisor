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
// navigates to sections with both description of the article and link to its pdf
const publications = document.getElementsByClassName("gs_r gs_or gs_scl");


if (publications) {
    for (let i = 0; i < publications.length; i++) {
//        checks whether founded publication has link to the pdf
        const publication_pdf = publications[i].getElementsByClassName("gs_ggs gs_fl");

        if (publication_pdf.length === 1) {
//            location of class containing article title
            const publication_info = publications[i].getElementsByClassName("gs_rt");
            const location = publication_info[0].children.length
            const publication_title = publication_info[0].children[location-1]['innerText'];

            const create_graph = document.createElement("button");
            create_graph.className = "collapsible";
            create_graph.textContent = `project button`;

            const drawing_board = document.createElement("div");
            drawing_board.innerHTML = "<p>"+publication_title+"</p>";
            drawing_board.className = "content";
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

            publication_pdf[0].insertAdjacentElement("beforeend", create_graph);
            search_result_box = publication_pdf[0].parentNode;
            links_of_result = search_result_box.getElementsByClassName('gs_fl');
            links_of_result[1].insertAdjacentElement('afterend', drawing_board)
        }
    }
}