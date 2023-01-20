class ArticleData {
    constructor(title, authors) {
        this.title = title;
        this.authors = authors;
    }
}

class PdfUrl {
    constructor(url) {
        this.url = url;
    }
}

function get_title(scholar_result) {
    const title_box = scholar_result.getElementsByClassName("gs_rt")
    var title = title_box[0].innerText
    if (title.startsWith('[')) {
        title = title.split('] ')
        title.shift()
        console.log(title)
        title = title.join('')
    }
    return title;
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

export function extract_pdf_url(scholar_result) {
    const pdf_url = scholar_result.getElementsByClassName("gs_or_ggsm")[0].firstChild.getAttribute("href");
    return new PdfUrl(pdf_url);
}

// https://medium.com/meta-box/how-to-send-get-and-post-requests-with-javascript-fetch-api-d0685b7ee6ed
const request = (url, params = {}, method = 'GET') => {
    let options = {
        method
    };
    if ('GET' === method) {
        url += '?' + (new URLSearchParams(params)).toString();
    } else {
        options.body = JSON.stringify(params);
    }
    console.log(url);
    return fetch(url, options).then(response => response.json());
};

export const get = (url, params) => request(url, params, 'GET');
export const post = (url, params) => request(url, params, 'POST');