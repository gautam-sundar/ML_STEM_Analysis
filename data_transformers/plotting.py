import pandas as pd
import matplotlib.pyplot as plt


def univariate_plot(variable, value_dist, value_encodings, supress_nan=True):
    fig = plt.figure(figsize=(13, 7))
    ax = plt.axes()
    position, height = zip(*value_dist[variable].items())
    ax.bar(value_encodings[variable].transform(position), height)
    ax.set(xlabel='Values', ylabel='Frequency', title=variable)
    
    return pd.DataFrame({'Value': list(value_encodings[variable].classes_),
                         'Encoding': range(0, len(value_encodings[variable].classes_))},
                        columns=['Value', 'Encoding'])