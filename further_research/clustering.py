from sklearn.cluster import KMeans

def get_centroids(current_labels,dists):
    current_labels[dists[:,0].argmin()] = 3
    current_labels[dists[:,1].argmin()] = 4
    current_labels[dists[:,2].argmin()] = 5

def k_centroids(vectors, k=3):
    for row in vectors:
        for element in row:
            if type(element) == str:
                print(row)
    k_means = KMeans(n_clusters=k).fit(vectors)
    dists = k_means.transform(vectors)
    get_centroids(k_means.labels_,dists)

    return k_means.labels_

