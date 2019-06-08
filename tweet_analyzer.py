import collections
import itertools
import re

import numpy as np
import pandas as pd


class TweetAnalyzer:
    """
    Functionality for analyzing and categorizing content from tweets.

    Attributes
    ----------
        self.__stop_words (list): List of unnecessary link words and the user's hashtags for analysis purposes.
        self.status_bar (QTextBrowser): Status bar @ the bottom of UI (A reference of App statusbar_table's object.)

    Methods
    -------
        __init__(self, ,main_window): Initialize Class Attributes.
        tweets_to_data_frame(self, tweets): Get tweets from tweeter's api and extract it into a data frame.
        remove_url(self, text): Remove url from the tweet.
        word_counter(self, tweets, tag): A method to count the popular words.
        word_counter_to_data_frame(self, df, word_count_df): A method to insert the word counter analasis into a
                                data frame.
        user_source_counter_to_data_frame(self, df, source_count_df): A method to insert the popular word counter's
                                analysis into a data frame
        words_counter_graph(self, workbook, worksheet, word_count_df, tag): Creates a graph of popular words for
                                each hashtag.
        user_source_graph(self, workbook, worksheet, df, tag): creates a graph of most common user's source.

    """

    def __init__(self, main_window):

        """Initializing TweetAnalyzer Class"""
        self.__stop_words = None
        self.status_bar = main_window.get_statusbar_table

    def tweets_to_data_frame(self, tweets):

        """
        Copy data to dataframe in order to export it into excel file.

        Args:
            tweets (list): A list which stored the tweets of specific hashtag at a moment.

        Parameters:
            df (DataFrame): Stores the data extracted from the tweets.

        Returns:
            df (DataFrame): Stores the data extracted from the tweets.
        """

        try:

            # Copies the Tweets's actual text.
            df = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['tweets'])
            # Copies Data according to df's title.
            df['User'] = np.array([tweet.user.screen_name for tweet in tweets])
            df['Followers'] = np.array([tweet.user.followers_count for tweet in tweets])
            df['Friends'] = np.array([tweet.user.friends_count for tweet in tweets])
            df['User Joined'] = np.array([tweet.user.created_at for tweet in tweets])
            df['Location'] = np.array([tweet.user.location for tweet in tweets])
            df['Tweet ID'] = np.array([tweet.id_str for tweet in tweets])
            df['Tweet Length'] = np.array([len(tweet.full_text) for tweet in tweets])
            df['Date'] = np.array([tweet.created_at for tweet in tweets])
            df['Source'] = np.array([tweet.source for tweet in tweets])
            df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
            df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])

            return df

        except Exception as e:
            # Clear The Status Bar
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def remove_url(self, text):

        """
        Remove url from the tweet.

        Args:
            text (str): the tweet.

        Parameters:
            None

        Returns:
            A text string which has no url inside.
        """

        try:

            return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", text).split())

        except Exception as e:
            # Clear The Status Bar
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def word_counter(self, tweets, tag):

        """
        A method to count the popular words for each hashtag in the list.

        Args:
            self: To use stop words attribute.
            tweets (list): List of tweets objects
            tag (str): The current hashtag from the list.

        Parameters:
            clean_tweets (list): List of tweets without their url inside.
            words_in_tweet (list): Taking the tweets from clean_tweets and makes it with lowercase and split the
                                   words for each tweet into a list.
            tweets_nsw (list): List of Words without the stop words.
            all_words (list): List of all words across tweets.
            counts_no_urls (Counter): Creates a counter to gauge the quantity for each word/
            clean_tweets_df (DataFrame): Creates a Pandas Data Frame with amount limitation of common words
            english_stop_words (list): English stop words.
            __stop_words (set): Set of english stop words.
        Returns:
             clean_tweets_df (DataFrame): Creates a Pandas Data Frame with amount limitation of common words
        """

        try:
            # Remove Urls from original tweet
            clean_tweets = [self.remove_url(tweet.full_text) for tweet in tweets]

            # Make all elements in the list lowercase
            words_in_tweet = [tweet.lower().split() for tweet in clean_tweets]

            # List all the Stop words in english & our search hashtags in order to remove it
            if self.__stop_words is None:
                #nltk's stop words doesnt compile into exe file...
                english_stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
                              "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
                              'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
                              'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
                              'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                              'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
                              'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                              'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
                              'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                              'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                              'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                              'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
                              'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
                              'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',
                              "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
                              "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
                              "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
                self.__stop_words = set(english_stop_words)
                self.__stop_words.add('RT'.lower())  # in case of retweet start
                # Options to add in the future... 'RT @'

            # Add the hashtag without '#'
            self.__stop_words.add(tag[1:])

            # New List of Words without the stop words/
            tweets_nsw = [[word for word in tweet_words if not word in self.__stop_words]
                          for tweet_words in words_in_tweet]

            # List of all words across tweets
            all_words = list(itertools.chain(*tweets_nsw))

            # Create counter
            counts_no_urls = collections.Counter(all_words)

            # Create a Pandas Data Frame with amount limitation of common words
            clean_tweets_df = pd.DataFrame(counts_no_urls.most_common(5), columns=['Words', 'Count'])

            return clean_tweets_df

        except Exception as e:
            # Clear The Status Bar
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def word_counter_to_data_frame(self, df, word_count_df):

        """
        Adding A space Between Rows & Creating Data Frame of Words Count
        for future extraction to Excel File.

        Args:
           df (DataFrame): Main DataFrame with all the relevant data.
           word_count_df (DataFrame): A dataframe that contains the list of popular words and their quantity.

        Parameters:
            No Parameters.

        Returns:
             df (DataFrame): Main DataFrame with all the relevant data.
        """

        try:

            # Creates Space between columns.
            df[' '] = " "

            df['Popular Words'] = word_count_df['Words']
            df['Count'] = word_count_df['Count']

            # Creates Space between columns.
            df['  '] = " "

            return df

        except Exception as e:
            # Clear The Status Bar
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def user_source_counter_to_data_frame(self, df, source_count_df):

        """
        Adding A space Between Rows & Creating Data Frame of Source Count
        for future extraction to Excel File.

        Args:
           df (DataFrame): Main DataFrame with all the relevant data.
           source_count_df (DataFrame): A dataframe that contains the list of most user's source.

        Parameters:
            source_count_dict (dict) = A dictionary that contains the list of top users's source and their quantity.

        Returns:
             df (DataFrame): Main DataFrame with all the relevant data.
        """

        try:

            source_count_dict = dict(source_count_df)

            # Source Type
            df['Unique Source'] = pd.DataFrame(data=[key for key in source_count_dict.keys()])

            # Source Amount
            df['Source Count'] = pd.DataFrame(data=[value for value in source_count_dict.values()])

            # Creates Space between columns.
            df['   '] = " "

            return df

        except Exception as e:
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def words_counter_graph(self, workbook, worksheet, word_count_df, tag):

        """
        Creates a Chart inside excel file of Popular Words analysis.
        Takes data that copied before from specific two consecutive cells.

        Args:
            workbook (Workbook): Get the xlsxwriter objects from the dataframe writer object.
            worksheet (Worksheet):  Object for the Excel worksheet which has the ability to insert items.
            word_count_df (DataFrame): A dataframe that contains the list of popular words and their quantity.
            tag (str): Current Hashtag.

        Parameters:
            chart (Workbook): Graph that will display the data sample

        Returns:
            None
        """

        try:
            # Create a chart object.
            chart = workbook.add_chart({'type': 'column'})

            # Add a chart title.
            chart.set_title({'name': 'Popular Words'})

            # Configure the series of the chart from specific cells inside the excel file.

            chart.add_series({
                'categories': "=" + "'" + tag + "'" + '!$O$2:$O$' + str(len(word_count_df['Words'])),
                'values': "=" + "'" + tag + "'" + '!$P$2:$P$' + str(len(word_count_df['Words'])),
                'gap': 10,
            })

            # Configure the chart axes.
            chart.set_x_axis({'name': 'Words'})
            chart.set_y_axis({'name': 'Count'})

            # Turn off chart legend. It is on by default in Excel.
            chart.set_legend({'position': 'none'})

            # Insert the chart into the worksheet.
            worksheet.insert_chart('W1', chart)

        except Exception as e:
            # Clear The Status Bar
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))

    def user_source_graph(self, workbook, worksheet, df, tag):

        """
        Creates a Chart inside excel file of Most User's Source analysis.
        Takes data that copied before from specific two consecutive cells.

        Args:
            workbook (Workbook): Get the xlsxwriter objects from the dataframe writer object.
            worksheet (Worksheet):  Object for the Excel worksheet which has the ability to insert items.
            df (DataFrame): Main DataFrame with all the relevant data.
            tag (str): Current Hashtag.

        Parameters:
            graph (Workbook): Graph that will display the data sample

        Returns:
            None

        """
        try:
            # Create a pie graph object
            graph = workbook.add_chart({'type': 'pie'})

            # Configure the pie graph with categories & values from the specific df
            graph.add_series({
                'name': 'Most UserSource',
                'categories': "='" + tag + "'!$R$2:$R$" + str(len(df['Unique Source'])),
                'values': "='" + tag + "'!$S$2:$S$" + str(len(df['Source Count'])),
                'points': [
                    {'fill': {'color': '#5ABA10'}},
                    {'fill': {'color': '#FE110E'}},
                    {'fill': {'color': '#CA5C05'}},
                ],
            })

            # Add a graph title.
            graph.set_title({'name': 'User Source'})

            # Insert the graph into the worksheet (with an offset)
            worksheet.insert_chart('AE1', graph)

        except Exception as e:
            self.status_bar.clear()
            self.status_bar.append('<center>Error Has Occurred: {0}'.format(e))