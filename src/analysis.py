#!/usr/bin/env python

import numpy as np
import pandas as pd
import itertools
from sklearn.ensemble import RandomForestClassifier
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

## Predict the tendency for articles to be in the top half of organic traffic 
## given a range of feature values, feature name, test set and random forest
## classifier

def predict_traffic(x_range, feature, test_data, forest):
    print("Predicting for '" + feature.lower() + "'...")
    
    for cur_x in x_range:
        test_subset = test_data.loc[(test_data[feature] == cur_x) & (test_data["Prediction"] == 0), ["Content Length", "Title Length", "Links", "Verbosity", "Sentiment"]]
        test_data.loc[(test_data[feature] == cur_x) & (test_data["Prediction"] == 0), "Prediction"] = forest.predict(test_subset) 
    

## Train random forest and save predictions to ../models/predictions.csv

def main():
    # import data
    posts = pd.read_json("../data/wp_posts.json")
    analytics = pd.read_csv("../data/analytics2020.csv")
    
    # reformat page names from Google Analytics
    for i_post, row1 in posts.iterrows():
        for i_analytics, row2 in analytics.iterrows():
            if posts.loc[i_post, "post_name"] in analytics.loc[i_analytics, "Landing Page"] and "/?" not in analytics.loc[i_analytics, "Landing Page"]:
                analytics.loc[i_analytics, "Landing Page"] = posts.loc[i_post, "post_name"]
            

    # filter columns and merge data from MySQL/Google Analytics
    analytics.rename(columns={"Landing Page": "post_name"}, inplace=True)
    analytics = analytics.filter(["post_name", "Users", "Bounce Rate", "Pages / Session"])
    data = posts.merge(analytics, on="post_name")
    data.rename(columns={"post_name": "Post", "post_title": "Title", "post_content": "Content", "Bounce Rate": "Bounced", "Pages / Session": "Pages"}, inplace=True)
    
    # convert to appropriate data types, calculate additional features
    data["Users"] = data.apply(lambda post: int(post["Users"].replace(",", "")), axis=1)
    data["Bounced"] = data.apply(lambda post: float(post["Bounced"].replace("%", "")), axis=1)
    data["Pages"] = data.apply(lambda post: float(post["Pages"]), axis=1)
    data["Content Length"] = data.apply(lambda post: len(BeautifulSoup(post["Content"], "html5lib").get_text().split()), axis=1)
    data["Title Length"] = data.apply(lambda post: len(post["Title"]), axis=1)
    data["Links"] = data.apply(lambda post: len(BeautifulSoup(post["Content"], "html5lib").find_all("a")), axis=1)
    data["Verbosity"] = data.apply(lambda post: len(word_tokenize(BeautifulSoup(post["Content"], "html5lib").get_text())) / len(sent_tokenize(BeautifulSoup(post["Content"], "html5lib").get_text())), axis=1)
    sentiment = SentimentIntensityAnalyzer()
    data["Sentiment"] = data.apply(lambda post: sentiment.polarity_scores(post["Content"])["compound"], axis=1)
    data["Top"] = data.apply(lambda post: post["Users"] >= data["Users"].quantile(.50), axis=1)
    
    # train random forest
    print("Training random forest...")
    forest = RandomForestClassifier(oob_score=True, max_features="sqrt", n_estimators=500)
    forest.fit(data[["Content Length", "Title Length", "Links", "Verbosity", "Sentiment"]], data["Top"])
    print("\tOOB score: " + str(forest.oob_score_))
    print("\tFeature importances: " + str(forest.feature_importances_))
    #importance_sd = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    #print(importance_sd)
    #quit()
    
    # create test set 
    test_data = pd.DataFrame(list(itertools.product(np.arange(300, 2100, 100),
                                                    np.arange(data["Title Length"].min(), data["Title Length"].max() + 1),
                                                    np.arange(data["Links"].min(), data["Links"].max() + 1),
                                                    np.linspace(data["Verbosity"].min(), data["Verbosity"].max(), 10),
                                                    np.linspace(data["Sentiment"].min(), data["Sentiment"].max(), 10))))
    test_data.rename(columns={0: "Content Length", 1: "Title Length", 2: "Links", 3: "Verbosity", 4: "Sentiment"}, inplace=True)
    test_data["Prediction"] = np.zeros(len(test_data.index))
     
    # plot marginal probabilities of articles with certain features having above-average traffic
    predict_traffic(np.arange(300, 2100, 100), "Content Length", test_data, forest)
    predict_traffic(np.arange(data["Title Length"].min(), data["Title Length"].max() + 1), "Title Length", test_data, forest)
    predict_traffic(np.arange(data["Links"].min(), data["Links"].max() + 1), "Links", test_data, forest)
    predict_traffic(np.linspace(data["Verbosity"].min(), data["Verbosity"].max(), 10), "Verbosity", test_data, forest)
    predict_traffic(np.linspace(data["Sentiment"].min(), data["Sentiment"].max(), 10), "Sentiment", test_data, forest)

    test_data.to_csv("../models/predictions.csv")

if __name__ == "__main__":
    main()