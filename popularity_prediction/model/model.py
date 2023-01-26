import pandas as pd
import matplotlib.pyplot as plt



if __name__=='__main__':
    df = pd.read_csv(open('semanticscholar_results.csv',encoding='UTF-8'))
    plt.hist(df['citationcount'].tolist())
    plt.yscale('log')
    plt.show()