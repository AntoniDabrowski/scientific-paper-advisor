class ArticleData {
    constructor(title, authors) {
        this.title = title;
        this.authors = authors;
    }
}

function get_title(scholar_result) {
    const title_box = scholar_result.getElementsByClassName("gs_rt")
    return title_box[0].firstChild.innerText;
}

function get_author(scholar_result) {
    const author_box = scholar_result.getElementsByClassName("gs_a")
    const authors_line = author_box[0].innerText.split('-')[0]
    return authors_line.split(',');
}


export function extract_article_data(scholar_result) {
    const title = get_title(scholar_result)
    const author = get_author(scholar_result)

    return new ArticleData(title, author);
}