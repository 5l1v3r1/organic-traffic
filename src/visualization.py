#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


## Plot the tendency for articles to be in the top half of organic traffic 
## given an axes, range of feature values, feature name and set of predictions 

def plot_feature(ax, x_range, feature, test_data):
    print("Plotting " + feature.lower() + "...")
    user_predictions = np.empty(0)
    
    for cur_x in x_range:
        cur_prediction = test_data.loc[test_data[feature] == cur_x, "Prediction"] 
        user_predictions = np.append(user_predictions, sum(cur_prediction) / len(cur_prediction))

    ax.set_ylim(0, 1)
    ax.plot(x_range, user_predictions, linewidth=3, color='green')


## Visualize predictions for varying values of content length, title length, 
## number of outbound links, average sentence length and sentiment

def main():
    # import data
    test_data = pd.read_csv("../models/predictions.csv")

    # plot marginal probabilities that articles with specified features will have above-average traffic
    fig = plt.figure(figsize=(12, 4))    
    ax1 = fig.add_subplot(151)
    ax1.set_xlabel("Words in Article", fontdict={'weight': 'bold'}, labelpad=7)
    ax1.set_ylabel("Tendency to Have High Organic Traffic", fontdict={'weight': 'bold'}, labelpad=7)
    ax1.set_facecolor("lightgrey")
    plot_feature(ax1, np.arange(300, 2100, 100), "Content Length", test_data)
    ax2 = fig.add_subplot(152)
    ax2.set_xlabel("Words in Title", fontdict={'weight': 'bold'}, labelpad=7)
    ax2.set_facecolor("lightgrey")
    plot_feature(ax2, np.arange(test_data["Title Length"].min(), test_data["Title Length"].max() + 1), "Title Length", test_data)
    ax2.yaxis.set_ticks([])
    ax3 = fig.add_subplot(153)
    ax3.set_xlabel("Outbound Links", fontdict={'weight': 'bold'}, labelpad=7)
    ax3.set_facecolor("lightgrey")
    plot_feature(ax3, np.arange(test_data["Links"].min(), test_data["Links"].max() + 1), "Links", test_data)
    ax3.yaxis.set_ticks([])
    ax4 = fig.add_subplot(154)
    ax4.set_xlabel("Average Sentence Length", fontdict={'weight': 'bold'}, labelpad=7)
    ax4.set_facecolor("lightgrey")
    plot_feature(ax4, test_data["Verbosity"].unique(), "Verbosity", test_data)
    ax4.yaxis.set_ticks([])
    ax5 = fig.add_subplot(155)
    ax5.set_xlabel("Sentiment", fontdict={'weight': 'bold'}, labelpad=7)
    ax5.set_facecolor("lightgrey")
    plot_feature(ax5, test_data["Sentiment"].unique(), "Sentiment", test_data)
    ax5.yaxis.set_ticks([])
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()