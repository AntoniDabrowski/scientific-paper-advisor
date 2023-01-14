var Plotly = require('plotly.js-strict-dist')

function create_text_for_graph(nodes) {
    let result = [];

    for (let i = 0; i < nodes.length; i++) {
        let node_dict = nodes[i]
        result.push(`<a href="${node_dict['url']}">${node_dict['title']}</a>` +
            `<br>Authors: ${node_dict['authors']}<br>#citations: ${node_dict['num_publications']}`)
    }

    return result;
}

function create_edges_between_articles(links, layout) {
    let results = []
    for (let i = 0; i < links.length; i++) {
        results.push({
            x: [layout[links[i]['source']][0], layout[links[i]['target']][0]],
            y: [layout[links[i]['source']][1], layout[links[i]['target']][1]]
        })
    }
    return results;
}

function prepare_article_markers(layout, nodes) {
    let x = [];
    let y = [];
    let point_size = [];
    for (let key in layout) {
        x.push(layout[key][0])
        y.push(layout[key][1])
    }
    for (let i = 0; i < nodes.length; i++) {
        point_size.push(Math.log(nodes[i]['num_publications']))
    }

    const text = create_text_for_graph(nodes)

    return {
        x: x,
        y: y,
        text: text,
        mode: 'markers',
        marker: {
            size: point_size,
            sizemode: 'area'
        }
    };
}

export function create_graph_on_scholar_result(divid, json) {
    console.debug(json)

    const articles_markers = prepare_article_markers(json.layout, json.nodes)
    const citation_edges = create_edges_between_articles(json.links, json.layout)
    const layout = {
        showlegend: false,
        xaxis: {
            visible: false
        },
        yaxis: {
            visible: false
        },
        aaxis: {
            showgrid: true
        }
    }

    const graph_data = [articles_markers].concat(citation_edges)
    Plotly.newPlot(divid, graph_data, layout)
}


export function purge_graph(divid) {
    Plotly.purge(divid)
}

