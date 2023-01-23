var Plotly = require('plotly.js-strict-dist')
import categories from './categories.json' assert {type: 'json'};

function create_text_for_graph(nodes) {
    let result = [];

    for (let i = 0; i < nodes.length; i++) {
        let node_dict = nodes[i]
        result.push(`<a href="${node_dict['url']}">${node_dict['title']}</a>` +
            `<br>Authors: ${node_dict['authors']}<br>#citations: ${node_dict['num_publications']}`)
        // TODO: Move reference to url to the node, rather than its hover
        // TODO: Hovers by default has part '<extra>something</extra>', where 'something' will be display next to hover, we don't want that
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
        point_size.push(nodes[i]['num_publications'])
    }

    const text = create_text_for_graph(nodes);

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
    // TODO: After user clicks on node, the related PDF should pop-up
}

export function create_scatter_on_scholar_result(scatter, json) {
    var data = [];
    var title = "";
    var colorway = [];
    Object.entries(json).forEach(entry => {
        const [key, value] = entry;
        var join_arr = [];
        for (var i=0; i<value.text.length; i++)
            join_arr[i] = [value.text[i], value.url[i]];
        var trace = {
            x: value.x,
            y: value.y,
            z: value.z,
            type: 'scatter3d',
            text: value.text,
            name: key,
            mode: 'markers',
            marker: { size: 4 },
            customdata: join_arr,
            hovertemplate: '%{customdata[0]}<extra></extra>'
        };
        colorway.push(value.color);
        data.push(trace);
        title = value.title;
    });

    var layout = {
        title: 'Further research clustering - ' + categories[title],
        hoverlabel: { align:'left' },
        colorway: colorway,
        width: 1000,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 30,
            pad: 0
        },
        xaxis: {
            title: 'x',
            showgrid: false,
            zeroline: false
        },
        yaxis: {
            title: 'y',
            showline: false
        },
        zaxis: {
            title: 'z',
            showline: false
        }
    };
    Plotly.newPlot(scatter.id, data, layout);

    // Opens PDF related to the clicked point
    scatter.on('plotly_click', function(data){
        window.open(data['points'][0]['customdata'][1]);
    });
}

export function purge_graph(divid) {
    Plotly.purge(divid)
}

