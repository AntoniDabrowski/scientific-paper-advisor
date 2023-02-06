from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE


def parse_hovers(docs):
    hovers = []

    for doc in docs:
        new_doc = ""
        current_line = ""
        for word in doc.split():
            if len(current_line) + len(word) > 100:
                new_doc += current_line + '<br>'
                current_line = ""
            current_line += ' ' + word
        if current_line:
            new_doc += current_line + '<br>'
        hovers.append(new_doc)
    return hovers


def remove_outliers(reduced_vectors, labels, hovers):
    center = reduced_vectors.mean(axis=0)

    MSE = [np.mean((center - vector) ** 2) for vector in reduced_vectors]

    avg_MSE = np.mean(MSE)
    std_MSE = np.std(MSE)

    new_vectors = []
    new_labels = []
    new_hovers = []

    for vector, label, hover, MSE_single in zip(reduced_vectors, labels, hovers, MSE):
        if MSE_single < avg_MSE + 2 * std_MSE:
            new_vectors.append(vector)
            new_labels.append(label)
            new_hovers.append(hover)

    return np.array(new_vectors), new_labels, new_hovers


def show_results_3D(reduced_vectors, labels, hovers, plot_name):
    df = pd.DataFrame(data={
        'x': reduced_vectors[:, 0],
        'y': reduced_vectors[:, 1],
        'z': reduced_vectors[:, 2],
        'labels': [str(label) for label in labels],
        'hover': hovers
    })

    fig = px.scatter_3d(df,
                        x='x',
                        y='y',
                        z='z',
                        color='labels',
                        custom_data=['hover'],
                        color_discrete_map={
                            "A": 'rgb(255, 150, 150)',
                            "B": 'rgb(150, 255, 150)',
                            "C": 'rgb(150, 150, 255)',
                            "A_centroid": "red",
                            "B_centroid": "green",
                            "C_centroid": "blue"})

    fig.update_layout(
        hoverlabel=dict(
            font_size=12
        ),
        title=f'Further research clustering - {plot_name}',
        showlegend=False
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}",
        marker_size=4
    )

    fig.show()

def show_results_2D(reduced_vectors, labels, hovers, plot_name):
    df = pd.DataFrame(data={
        'x': reduced_vectors[:, 0],
        'y': reduced_vectors[:, 1],
        'labels': [str(label) for label in labels],
        'hover': hovers
    })

    fig = px.scatter(df,
                    x='x',
                    y='y',
                    color='labels',
                    custom_data=['hover'],
                    color_discrete_map={
                        "A": 'rgb(255, 150, 150)',
                        "B": 'rgb(150, 255, 150)',
                        "C": 'rgb(150, 150, 255)',
                        "A_centroid": "red",
                        "B_centroid": "green",
                        "C_centroid": "blue"},
                    width=600,
                    height=600)

    fig.update_layout(
        hoverlabel=dict(
            font_size=12
        ),
        title=f'Further research clustering - {plot_name}',
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}",
        marker_size=4
    )

    fig.show()

def show_results(reduced_vectors_PCA, reduced_vectors_TSNE, labels, hovers, plot_name):
    df_PCA = pd.DataFrame(data={
        'x': reduced_vectors_PCA[:, 0],
        'y': reduced_vectors_PCA[:, 1],
        'labels': [str(label) for label in labels],
        'hover': hovers,
        'alg': ['PCA'] * reduced_vectors_PCA.shape[0]
    })

    df_TSNE = pd.DataFrame(data={
        'x': reduced_vectors_TSNE[:, 0],
        'y': reduced_vectors_TSNE[:, 1],
        'labels': [str(label) for label in labels],
        'hover': hovers,
        'alg': ['t-SNE'] * reduced_vectors_TSNE.shape[0]
    })

    df = pd.concat([df_PCA, df_TSNE], axis=0)

    fig = px.scatter(df,
                     x='x',
                     y='y',
                     color='labels',
                     custom_data=['hover'],
                     color_discrete_map={
                         "A": 'rgb(255, 150, 150)',
                         "B": 'rgb(150, 255, 150)',
                         "C": 'rgb(150, 150, 255)',
                         "A_centroid": "red",
                         "B_centroid": "green",
                         "C_centroid": "blue"},
                     width=1000,
                     height=500,
                     facet_col="alg")

    fig.update_layout(
        hoverlabel=dict(
            font_size=12
        ),
        # yaxis=dict(automargin=True),
        # margin=dict(l=20, r=170, t=70, b=20),
        title={
            'text': f'Further research clustering - {plot_name}',
            'x': 0.5,
            'xanchor': 'center'
        },
        # title=f'Further research clustering - {plot_name}',
        showlegend=False
    )

    def update(axis):
        axis.update(matches=None)
        axis.showticklabels = True

    fig.for_each_yaxis(update)
    fig.for_each_xaxis(update)

    fig.update_traces(
        hovertemplate="%{customdata[0]}",
        marker_size=6
    )

    fig.show()

def PCA_vs_TSNE(vectors, labels, docs, plot_name=''):
    model = PCA(n_components=2)
    model.fit(vectors)
    reduced_vectors_PCA = model.transform(vectors)

    model = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=3)
    reduced_vectors_TSNE = model.fit_transform(vectors)

    hovers = docs.values()
    hovers = parse_hovers(hovers)
    show_results(reduced_vectors_PCA, reduced_vectors_TSNE, labels, hovers, plot_name)


def dimensionality_reduction(vectors, labels, docs, alg='t-SNE', cut_outliers=False, show_plot=False, plot_name='',
                             dim=3):
    assert dim in [2,3]

    if alg == 'PCA':
        model = PCA(n_components=dim)
        model.fit(vectors)
        reduced_vectors = model.transform(vectors)
    elif alg == 't-SNE':
        # demonstrational purposes / won't work online
        model = TSNE(n_components=dim, learning_rate='auto', init='random', perplexity=3)
        reduced_vectors = model.fit_transform(vectors)
    else:
        raise ValueError(f"Dimensionality reduction can be only performed with algorithm PCA or t-SNE, not {alg}")

    hovers = docs.values()
    if cut_outliers and dim == 3:
        # demonstrational purposes / won't work online
        reduced_vectors, labels, hovers = remove_outliers(reduced_vectors, labels, hovers)

    if show_plot:
        hovers = parse_hovers(hovers)
        if dim == 3:
            show_results_3D(reduced_vectors, labels, hovers, plot_name)
        else:
            show_results_2D(reduced_vectors, labels, hovers, plot_name)
    return reduced_vectors, labels, model
