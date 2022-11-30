from scholarly import scholarly


def LCSubStr(X, Y):
    m = len(X)
    n = len(Y)
    LCSuff = [[0 for k in range(n + 1)] for l in range(m + 1)]
    result = 0

    for i in range(m + 1):
        for j in range(n + 1):
            if (i == 0 or j == 0):
                LCSuff[i][j] = 0
            elif (X[i - 1] == Y[j - 1]):
                LCSuff[i][j] = LCSuff[i - 1][j - 1] + 1
                result = max(result, LCSuff[i][j])
            else:
                LCSuff[i][j] = 0
    return result


def is_it_right_article(title_a, title_b):
    common_len = LCSubStr(title_a, title_b)
    avr_len = (len(title_a) + len(title_b)) / 2
    return common_len > 0.6 * avr_len


def get_pub(title):
    search_query = scholarly.search_pubs(title)
    pub = next(search_query)

    if not is_it_right_article(title, pub['bib']['title']):
        return {}
    return pub


def get_citations(arg):
    if type(arg) == dict:
        return scholarly.citedby(arg)
    elif type(arg) == str:
        pub = get_pub(arg)
        return scholarly.citedby(pub)
    else:
        raise ValueError("Argument has to be string (title) or dict (publication).")


def test_run():
    title = 'Reducing the time complexity of the derandomized evolution strategy with covariance matrix adaptation (CMA-ES)'

    pub = get_pub(title)
    cit = get_citations(pub)
    for i, c in enumerate(cit):
        print(c['bib']['title'])
        if i > 3:
            break
