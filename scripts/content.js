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
const results = document.getElementsByClassName("gs_ggs gs_fl")

if (results) {
    for (let i = 0; i < results.length; i++) {
        const create_graph = document.createElement("button");
        create_graph.textContent = `project button`;

        results[i].insertAdjacentElement("beforeend", create_graph);
    }

}