"""   Imports   """
import collections
from datetime import datetime
import itertools
import json
import re
import sys
import webbrowser
from nltk.corpus import stopwords
import time

import numpy as np
import pandas as pd

from PyQt5.QtCore import QSize
from PyQt5.QtGui import (QIcon, QPixmap, QImage, QPalette, QBrush)
from PyQt5.QtWidgets import (QTextBrowser, QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QAction, QFileDialog)

from tweepy import (API, Cursor, OAuthHandler, Stream, StreamListener, TweepError, RateLimitError)

import twitter_credentials


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
            df['Coordinates'] = np.array([tweet.coordinates for tweet in tweets])
            df['Tweet ID'] = np.array([tweet.id_str for tweet in tweets])
            df['Tweet Length'] = np.array([len(tweet.full_text) for tweet in tweets])
            df['Date'] = np.array([tweet.created_at for tweet in tweets])
            df['Source'] = np.array([tweet.source for tweet in tweets])
            df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
            df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
            df['    '] =''

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
                self.__stop_words = set(stopwords.words('english'))
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
                'categories': "=" + "'" + tag + "'" + '!$Q$2:$Q$' + str(len(word_count_df['Words'])),
                'values': "=" + "'" + tag + "'" + '!$R$2:$R$' + str(len(word_count_df['Words'])),
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
                'categories': "='" + tag + "'!$T$2:$T$" + str(len(df['Unique Source'])),
                'values': "='" + tag + "'!$U$2:$U$" + str(len(df['Source Count'])),
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


class App(QMainWindow):

    """ App Class for initializing the UI and its abilities.

    The user interface has many capabilities that enable ease of use and provide user experience.

    Attributes:
        __title (str): Windows Application's title.
        __icon (str):  Stores the icon image's path.
        __left, __top, __width, __height (int): Windows Application's Size & Screen positioning.
        __num_of_tweets (int): Stores the amount of tweets to be extracted.
        __tag_list (dictionary): Dictionary to store the user tags.
        __tweet_matrix (list): List of list which stores all the original tweets.
        __statusbar_table (QTextBrowser): Status var at the UI to inform the user about the actions.
        __twitter_client (API): API instance.
        __tweet_analyzer (TweetAnalyzer): Initialize TweetAnalyzer Object in order to use class's methods.

    Methods:
        super().__init__(): QMainWindow Base Class __init__ constructor.
        __twitter_client_auth(self): Initializing Twitter Client Authentication.
        __stream_tweets(self, hash_tag_list): Initialize a Stream & Use Search Engine with User's Hashtags.
        __start_session(self): Main Method which initializing Authentication,Stream & Analysis for the tweets and
                               extract all the data to Excel File.
        __copyrights_btn_links(self, name): A method designed to identify links for buttons serving the copyright part.
        __create_button(self, width, height, top, left, image, func, text=None): Generic Method for creating a button
                               in UI.
        __create_line(self, width, height, top, left, size, text): Generic Method for creating a line in UI.
        __create_text_browser(self, left, top, width, height, text_size): Generic Method for creating a text browser
                               in UI.
        __create_label(self, left, top, width, height, img_path): Generic Method for creating a label in UI.
        __insert_number_of_tweets_method(self): A method designed to set the amount of tweets to be exported for
                              each hashtag.
        __add_hashtag_method(self): A method designed to add an hashtag into hashtags list
        __remove_hashtag_method(self): A method designed to remove an hashtag from hashtags list
        __clear_hashtag_list(self): A method designed to clear/clean hashtags list
        __load_hashtag_from_json(self): Data Serialization - A Method designed to load hashtags list from a json file.
        __save_hashtag_to_json(self): Data Serialization - A Method designed to save hashtags list into a json file.
        __set_event_action(self, action, func): A method toe set an event action when occurred.
        __set_main_window_conf(self, width, height, brush_size, img_path): Main window configuration method.
        get_statusbar_table(self): Share current status_bar's object with TweetAnalyzer's object to update it.
        closeEvent(self, event): An Overriding Method designed to open a small window to make sure the user wants to
                                 exit the UI.
        __init_ui(): Initializing all components in the Application.
    """

    def __init__(self):

        """Initializing App Class"""

        super().__init__()
        self.__title = 'Twitter Data Mining Final Project'
        self.__icon = 'images/icon.ico'
        self.__left = 50
        self.__top = 35
        self.__width = 1280
        self.__height = 680
        self.__num_of_tweets = 0
        self.__tag_list = dict()
        self.__tweet_matrix = list()
        self.__statusbar_table = self.__create_text_browser(250, 485, 800, 50, "font-size: 30px;")
        self.__twitter_client = None
        self.__tweet_analyzer = None
        self.__init_ui()

    def __twitter_client_auth(self):

        """
        Client Authentication with Twitter's API

        Args:
            No Args

        Parameters:
            self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
            App.auth (OAuthHandler): Stores the twitter credentials for authentication.
            App.twitter_client (API): API instance.

        Returns:
            App.twitter_client (API): API instance.
        """

        # Clean The Status Bar
        self.__statusbar_table.clear()

        try:

            # Initializing Twitter Client Authentication
            App.auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
            App.auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
            App.twitter_client = API(App.auth)

            # Checking if the authentication successful.
            assert App.twitter_client

            return App.twitter_client

        except AssertionError as a:
            self.__statusbar_table.append('<center>Assertion Error: {0}'.format(a))
        except Exception as e:
            self.__statusbar_table.append('<center>Authentication Error: {0}'.format(e))

    def __stream_tweets(self, hash_tag_list):

        """
        Initializing a Stream & Use Search Engine with User's Hashtags.

        Args:
            hash_tag_list (dict): Hashtags list itself for searching tweets.

        Parameters:
            self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
            App.listener (StreamListener): Initializing & stores StreamListener object.
            App.stream (Stream): Initializing & Store Stream object with auth & listener args.
            tweets_list[] (list): Temporary list in order to store specific hashtag's tweets
            self.__tweet_matrix (list): list of lists - Storing lists of tweets for each hashtag.

        Returns:
            None
        """

        # Clean The Status Bar
        self.__statusbar_table.clear()

        # Handles Twitter authetification and the connection to Twitter Streaming API
        App.listener = StreamListener()
        App.stream = Stream(App.auth, App.listener)

        # Capture the Tweets in a Temporary List
        tweets_list = []

        try:

            for hashtag, search_item in zip(hash_tag_list, range(1, len(hash_tag_list) + 1)):

                start = time.time()
                clock = time.clock()

                # Use Cursor to search for hashtag and copy it into a tweets_list
                for tweet in Cursor(self.__twitter_client.search, q=hashtag, result_type='mixed', tweet_mode='extended',
                                    include_entities=True, lang="en").items(self.__num_of_tweets):

                    # Capture a list of tweets
                    tweets_list.append(tweet)

                print("Search #{} took {} from {}".format(search_item, time.time() - start, clock))

                # Copy to the List of lists which stores all the tweets for each hashtags & clean the temp list
                self.__tweet_matrix.append(tweets_list.copy())
                tweets_list.clear()

        except RateLimitError as limit:
            self.__statusbar_table.append('<center>RateLimit Error: {0}'.format(limit))
        except TweepError as error:
            self.__statusbar_table.append('<center>Tweepy Error: {0}'.format(error))
        except Exception as e:
            self.__statusbar_table.append('<center>Search Error: {0}'.format(e))

        # Stream Disconnect
        App.stream.disconnect()

    def __start_session(self):

        """
        Main Method which initializing Authentication,Stream and Analysis in order to connect the Twitter API,
        Search for tweets for each hashtag, Extracting the data to an Excel file that for each tag has its own sheet
        and Creating charts from the data inside the Excel file after processing.

        Args:
            No Args.

        Parameters:
            self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
            self.__tag_list (dict): Hashtags list itself.
            self.__num_of_tweets (int): An integer which stores the amount of tweets to be exported.
            self.__twitter_client (API): API instance.
            #Remove tweet analayzer if still static
            self.__tweet_analyzer ('): Initializing TweetAnalyzer object in order to use its methods.
            writer (_XlsxWriter): Creates a Pandas Excel writer using XlsxWriter as the engine.
            workbook (Workbook): Get the xlsxwriter objects from the dataframe writer object.
            worksheet (Worksheet):  Object for the Excel worksheet which has the ability to insert items.
            df (DataFrame): A dataframe which storing all the data extracted from the tweets & their analysis.
            word_count_df (DataFrame): Creates Data Frame for each tag of Popular Words.
                                       Adds the Word Count Data Frame to the main Data Frame for future extraction.
            source_count_df (DataFrame): Creates Data Frame for the aamount of each User Source and
                                         Adds this Data Frame to the main Data Frame for future extraction.

        Methods:
            self.stream_tweets(self.__tag_list): Initialize a Stream & Use Search Engine with User's Hashtags.
            App.__twitter_client_auth(self): Initializing Twitter Client Authentication.
            self.__tweet_analyzer.tweets_to_data_frame(item): Extracting relevant information into a data frame.
            self.__tweet_analyzer.word_counter(item, tag): A method to count popular words for each hashtag.
            self.__tweet_analyzer.word_counter_to_data_frame(df, word_count_df): Adding A space Between Rows and
                                        Creating Data Frame of Words Count for future extraction to Excel File.
            self.__tweet_analyzer.words_counter_graph(workbook, worksheet, word_count_df, tag): Creates a bar graph
                                        within an Excel file with the analysis of the popular word.
            self.__tweet_analyzer.user_source_counter_to_data_frame(df, source_count_df): Adding A space Between Rows
                                        and Creating Data Frame of Source Count for future extraction to Excel File.
            self.__tweet_analyzer.user_source_graph(self, workbook, worksheet, df, tag): Creates a pie graph within
                                        an Excel file with the analysis of the most user source.

        Returns:
            None
        """

        # Clean The Status Bar
        self.__statusbar_table.clear()

        if self.__tag_list and self.__num_of_tweets > 0:

            try:

                # Creating a Stream Channel with Twitter API
                self.__twitter_client = App.__twitter_client_auth(self)
                self.__tweet_analyzer = TweetAnalyzer(self)
                self.__stream_tweets(self.__tag_list)

                if self.__tweet_matrix:

                    # Export information into an Excel file in format 'tweets_day_month_year_hour_minutes.xlsx'
                    writer = pd.ExcelWriter('tweets' + datetime.now().strftime("_%d_%m_%y_%H_%M") + '.xlsx',
                                            engine='xlsxwriter')
                    workbook = writer.book

                    for item, tag in zip(self.__tweet_matrix, self.__tag_list):

                        if len(item) > 0:
                            # Creates Data Frame for each hashtag
                            df = self.__tweet_analyzer.tweets_to_data_frame(item)

                            # Get Info about the amount for popular words
                            word_count_df = self.__tweet_analyzer.word_counter(item, tag)
                            df = self.__tweet_analyzer.word_counter_to_data_frame(df, word_count_df)

                            # Get Info about the amount from each User Source
                            source_count_df = df['Source'].value_counts()
                            df = self.__tweet_analyzer.user_source_counter_to_data_frame(df, source_count_df)

                            # Convert the dataframe to an XlsxWriter Excel object.
                            df.to_excel(writer, sheet_name=tag)
                            worksheet = writer.sheets[tag]

                            # Adds Popular Words's Graph
                            self.__tweet_analyzer.words_counter_graph(workbook, worksheet, word_count_df, tag)

                            # Adds Most User Source's Graph
                            self.__tweet_analyzer.user_source_graph(workbook, worksheet, df, tag)

                            # Reduce the zoom a little
                            worksheet.set_zoom(90)

                        else:

                            # Create Data Frame to inform the user that the specific hashtag couldn't be found
                            df = pd.DataFrame(data=["Couldn't Find Tweets For This Hashtag"], columns=['tweets'])
                            # Convert the dataframe to an XlsxWriter Excel object.
                            df.to_excel(writer, sheet_name=tag)

                    # Close the Pandas Excel writer and exit the Excel file.
                    writer.save()

                    self.__tweet_matrix.clear()

                    self.__statusbar_table.append("<center>Excel file was created successfully")

            except IndexError:
                print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            except SystemError as se:
                self.__statusbar_table.append("<center>SystemError has Occurred: {}".format(se))
            except Exception as e:
                self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

        else:
            self.__statusbar_table.append("<center>You Didn't Enter Hashtag or Number Of Tweets.")

    def __copyrights_btn_links(self, name):

        """   Copyrights Links Section

        At the bottom of UI there are button with image background which enable the option to contact me or visit
        my social media profiles.

        Args:
            name (str): Social media or contact link

        Parameters:
            contact_link (dict): A dictionary with social media or contact details & link.

        Returns:
            None

        """

        # Clean The Status Bar
        self.__statusbar_table.clear()

        contact_link = {'linkedin': 'https://www.linkedin.com/in/natylaza89/',
                        'github': 'https://github.com/natylaza89',
                        'gmail': 'mailto:natylaza89@gmail.com',
                        'facebook': 'https://www.facebook.com/naty.laza',
                        'twitter': 'https://twitter.com/natylaza89'}

        try:
            webbrowser.open(contact_link[name])

        except SystemError as se:
            self.__statusbar_table.append("<center>SystemError has Occurred: {}".format(se))
        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    def __create_button(self, width, height, top, left, image, func, text=None):

        """  Generic Pattern For Create Button

        Args:
           width, height, top, left (int): Size & Position of the button.
           image (str): Path of the background image.
           func (method): The function which be executed when the button clicked.
           text=None (str): A Text string for copyright button.

        Parameters:
            btn (QPushButton): The button with all the properties set.
            btn_image (QPixmap):  An object to store the background image for the button.

        Returns:
            btn (QPushButton): The button with all the properties set.

        """

        try:
            # Sets Button's Size & Position
            btn = QPushButton(self)
            btn.setFixedWidth(width)
            btn.setFixedHeight(height)
            btn.move(top, left)

            # Sets Button's Image
            btn_image = QPixmap(image)
            btn.setIcon(QIcon(btn_image))
            btn.setIconSize(QSize(200, 200))

            # Attach Function to a Button according to func & text arguments
            if text:
                btn.clicked.connect(lambda checked: self.__copyrights_btn_links(text))
            else:
                btn.clicked.connect(func)

            return btn

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def __create_line(self, width, height, top, left, size, text):

        """   Pattern For Create Line

        Args:
           width, height, top, left (int): Size & Position of the line.
           size (int): An integer to determine the size of the text.
           text (str): A Text string for a default display inside the line edit.

        Parameters:
            line (QLineEdit): The line with all the properties set.

        Returns:
            line (QLineEdit): The line with all the properties set.

        """
        try:
            # Sets Line's Size & Position
            line = QLineEdit(self)
            line.resize(width, height)
            line.move(top, left)

            # Sets Line's Default Text
            line.setPlaceholderText(text)

            # Sets Text's Size
            line.setStyleSheet("font-size: {}px;".format(size))

            return line

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def __create_text_browser(self, left, top, width, height, text_size):

        """   Pattern For Create Text Browser

        Args:
           left, top, width, height (int): Size & Position of the Text Broswer.
           text_size (str): An integer to determine the size of the text.

        Parameters:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        Returns:
            text_browser (QTextBrowser): The Text Browser with all the properties set.

        """

        try:

            text_browser = QTextBrowser(self)
            text_browser.setGeometry(left, top, width, height)
            text_browser.setStyleSheet(text_size)

            return text_browser

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def __create_label(self, left, top, width, height, img_path):

        """   Pattern For Create Text Browser

        Args:
           left, top, width, height (int): Size & Position of the Text Broswer.
           img_path (str): A text string to for image path.

        Parameters:
            label (QLineEdit): The label with all the properties set.

        Returns:
            label (QTextBrowser): The label with all the properties set.

        """

        try:

            label = QLabel(self)

            # Load Image & Resize it
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(QSize(width, height))

            # Set Image & Its Position
            label.setPixmap(pixmap)
            label.setGeometry(left, top, width, height)

            return label

        except Exception as e:
            print("Error Has Occurred: {}".format(e))

    def __insert_number_of_tweets_method(self):

        """ Sets the number of tweets to be export for each hashtag

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__numberoftweets_insert_line (QLineEdit): Input line which enable to get the number of tweets.
             text (str):  Gets the text from input line.
             self.__num_of_tweets (int): An integer to capture the number of tweets from the user.

        Returns:
            None

        """

        # Clean The Status Bar
        self.__statusbar_table.clear()

        try:

            # Gets the text from input line
            text = self.__numberoftweets_insert_line.text()

            # Checks the input validity and saves it
            if text.isdigit() and int(text) > 0:

                self.__num_of_tweets = int(self.__numberoftweets_insert_line.text())
                self.__statusbar_table.append("<center>Number Of Tweets Sets to " + str(int(text)) + "!.")

            else:
                raise ValueError("You Entered Wrong Input!")

        except ValueError as ve:
            self.__statusbar_table.append("<center>ValueError: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    def __add_hashtag_method(self):

        """ Add Hashtags For Future Search

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar at the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             self.__hashtag_line (QLineEdit): Input line to enable the user insert hashtags.

        Returns:
            None
        """

        # Clear Status Bar
        self.__statusbar_table.clear()

        try:

            # Gets the text from input line
            text = self.__hashtag_line.text()

            # Checks the input validity & Update The Display of Hashtags.
            if text:

                if text[0] == '#' and len(text) > 1:

                    # Adds the hashtag to the tag list table

                    if self.__tag_list.get(text) is None:

                        self.__tag_list[text] = text

                        # Clear Status Bar
                        self.__hashtag_table.clear()

                        # Updating the Hashtag Table in the UI
                        for tag in self.__tag_list:
                            self.__hashtag_table.append(tag)

                        # Update the user that the hashtags has been delelted
                        self.__statusbar_table.append('<center>{}'.format(text) + ' Has Been Added!')

                    else:
                        raise ValueError("Couldn't Add Because Of Duplicate Hashtag!")

                else:
                    raise ValueError("Wrong Input!")

            else:
                raise ValueError("Couldn't Add This Tag Because Its Empty!")

        except ValueError as ve:
            self.__statusbar_table.append("<center>ValueError: {}".format(ve))
        except Exception as e:
            self.__statusbar_table.append("<center>Error Has Occurred: {}".format(e))

    def __remove_hashtag_method(self):

        """ Remove hashtag from the list

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             self.__hashtag_line (QLineEdit): Input line to enable the user enter hashtags.

        Returns:
            None
        """

        # Status Bar
        self.__statusbar_table.clear()

        # Gets the text from input line
        text = self.__hashtag_line.text()

        try:

            del self.__tag_list[text]

            # Clear Hashtag Table & Status Bar
            self.__hashtag_table.clear()

            # Update Tag List Table
            for item in self.__tag_list:
                self.__hashtag_table.append(item)

            # Update the user that the hashtags has been delelted
            self.__statusbar_table.append("<center>{} Has Been Deleted!".format(text))

        except Exception as e:

            if text:
                self.__statusbar_table.append("<center>ValueError: {} Doesn't Exist, Couldn't Delete!".format(e))
            else:
                self.__statusbar_table.append("<center>ValueError: Empty Input - Couldn't Delete!")

    def __clear_hashtag_list(self):

        """ Clear the hashtag list in order to start over

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             self.__hashtag_line (QLineEdit): Input line to enable the user enter hashtags.

        Returns:
            None
        """

        # Clear Status bar & hashtag table
        self.__statusbar_table.clear()

        try:
            if len(self.__tag_list) > 0:

                # Clear the hashtag list
                self.__tag_list.clear()

                # Clear the Display of hashtag list @ the UI
                self.__hashtag_table.clear()

                # Update the user that the hashtag list has been deleted
                self.__statusbar_table.append('<center>Hashtag List Has Been Deleted!')

            else:
                raise Exception("Hashtag List is Already Empty!")

        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    def __load_hashtag_from_json(self):

        """  Data Serialization - A Method designed to load hashtags list from a json file.

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             file (QFileDialog) = An object that handles the json file.

        Returns:
            None
        """

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            file = QFileDialog.getOpenFileName(self, 'Open json File For Loading Hashtag List', "",
                                               "json file (*.json)")

            # Open the json file and load the hashtags
            with open(file[0], 'r') as f:

                if self.__tag_list is None:
                    self.__tag_list = json.load(f)
                else:
                    self.__tag_list = None
                    self.__tag_list = json.load(f)

            # Check validity of the data inside the json file - a list, empty dict or wrong input.
            if isinstance(self.__tag_list, list):
                raise FileExistsError(" The Hashtag List Inside Isn't Valid!")
            elif len(self.__tag_list) == 0:
                raise FileExistsError(" The Hashtag List Inside The File Is Empty!")

            else:
                for tag in self.__tag_list:
                    if tag[0] is not "#" or len(tag) < 2:
                        raise FileExistsError(" The Hashtag List Inside Isn't Valid!")

            # Clear the Hashtag Tabele in the UI
            self.__hashtag_table.clear()

            # Updating the Hashtag Table in the UI
            for tag in self.__tag_list:
                self.__hashtag_table.append(tag)

        except FileNotFoundError as fnfe:
            self.__statusbar_table.append("<center>File Not Found Error: {}".format(fnfe))
        except FileExistsError as fee:
            self.__statusbar_table.append("<center>File Exist Error: {}".format(fee))
        except Exception as e:
            self.__statusbar_table.append("<center>Error with Open File: {}".format(e))
        else:
            self.__statusbar_table.append("<center>Hashtag List Successfully Loaded!")

    def __save_hashtag_to_json(self):

        """ Data Serialization - A Method designed to save hashtags list into a json file.

        Args:
           No Args

        Parameters:
             self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
             self.__hashtag_table (QTextBrowser): Displays the hashtag list at the Top Left of UI.
             self.__tag_list (dictionary): Dictionary to store the user tags.
             file (QFileDialog) = An object that handles the json file.

        Returns:
            None
        """

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:

            if len(self.__tag_list) == 0:
                raise Exception(" The Hashtag List Is Empty!")

            else:
                file = QFileDialog.getSaveFileName(self, 'Create json File For Saving Hashtag List',
                                                   "hashtag_list" + datetime.now().strftime("_%d_%m_%y_%H_%M"),
                                                   "json file (*.json)")

                with open(file[0], 'w') as f:
                    json.dump(self.__tag_list, f)

        except FileNotFoundError as fnfe:
            self.__statusbar_table.append("<center>File Not Found Error: {}".format(fnfe))
        except FileExistsError as fee:
            self.__statusbar_table.append("<center>File Exist Error: {}".format(fee))
        except Exception as e:
            self.__statusbar_table.append("<center>Save File Error: {}".format(e))
        else:
            self.__statusbar_table.append("<center>Hashtags List Successfully Saved!")

    def closeEvent(self, event):

        """
        Close App Event(Overiding Method):

        Args:
           event (QCloseEvent): Close Event.

        Parameters:
             close (QMessageBox): A message box to interacte with the user before closing the UI.

        Returns:
            None
        """

        # Clear the Status bar
        self.__statusbar_table.clear()

        try:
            close = QMessageBox()

            close.setText("<center>Are You Sure?\n")
            close.setWindowTitle("Quit Window")
            close.setWindowIcon(QIcon(self.__icon))

            close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            close = close.exec()

            if close == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
                raise UserWarning(" Quit Canceled!")

        except UserWarning as uw:
            self.__statusbar_table.append("<center>UserWarning: {}".format(uw))
        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    def __set_event_action(self, action, func):

        """
        Configure an Event when it clicked

        Args:
           action (str): The Action to be executed.
           func (method): The method which has to be executed when this event occured.

        Parameters:
             event_action (QAction): An Object which nandels the event.

        Returns:
            None
        """

        try:

            event_action = QAction(action, self)
            event_action.triggered.connect(func)

        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    @property
    def get_statusbar_table(self):

        """
        Share Status Bar Object with TweetAnalyzer Object in order to infrom the user about actions's status.

        Args:
            No Args.

        Parameters:
            self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.

        Returns:
            self.__statusbar_table (QTextBrowser): Status bar @ the bottom of UI.
        """

        try:
            return self.__statusbar_table

        except Exception as e:
            self.__statusbar_table.append("<center>Error has Occurred: {}".format(e))

    def __set_main_window_conf(self, width, height, brush_size, img_path):

        """
        Configure Main Window of the UI.

        Args:
           width, height, brush_size: (int): An integers to configure the Size of the window & Brush size.
           img_path (str): A text string of the window background image path.

        Parameters:
             bg_image (QImage): An Object which nandels the background image.
             palette (QPalette): An Object which sets the background image at the main window app.

        Returns:
            None
        """

        try:
            self.setWindowIcon(QIcon(self.__icon))
            self.setWindowTitle(self.__title)
            self.setGeometry(self.__left, self.__top, self.__width, self.__height)

            bg_image = QImage(img_path)
            bg_image = bg_image.scaled(QSize(width, height))  # resize Image to widgets size

            # Sets the background image at the Main window App
            palette = QPalette()
            palette.setBrush(brush_size, QBrush(bg_image))  # 10 = Windowrole
            self.setPalette(palette)

        except Exception as e:
            print("Couldn't Set The Main Window Configuration Because: {}".format(e))

    def __init_ui(self):

        # Exit Button Configuration
        self.__set_event_action("Quit", self.closeEvent)

        # Main Window Configurtaion
        self.__set_main_window_conf(1500, 1024, 10, "images/background.png")

        """" Top Frame """

        # Banner\Logo
        self.__label = self.__create_label(200, 20, 900, 150, 'images/banner.png')

        """ Left Side """
        # Hashtag list Display
        self.__hashtag_table = self.__create_text_browser(175, 200, 350, 200, "font-size: 15px;")

        """ Center & Right Side """
        # Hashtag Edit Line, Add & Remove hashtags.
        self.__hashtag_line = self.__create_line(200, 40, 540, 200, 15, "Enter #hashtag...")
        self.__add_hashtag_button = self.__create_button(190, 40, 750, 200, 'images/add_hashtag.png',
                                                     self.__add_hashtag_method)
        self.__remove__hashtag_button = self.__create_button(190, 40, 950, 200, 'images/remove_hashtag.png',
                                                         self.__remove_hashtag_method)

        # Clear, Save & Load Hashtaglist
        self.__clear_hashtag_list_btn = self.__create_button(190, 40, 545, 250, 'images/clear_hashtag_list.png',
                                                         self.__clear_hashtag_list)
        self.__save_hashtag_list_btn = self.__create_button(190, 40, 750, 250, 'images/save_hashtag_list.png',
                                                        self.__save_hashtag_to_json)
        self.__load_hashtag_list_btn = self.__create_button(190, 40, 950, 250, 'images/load_hashtag_list.png',
                                                        self.__load_hashtag_from_json)

        # Number Of Tweets Insert Line
        self.__numberoftweets_insert_line = self.__create_line(200, 40, 540, 300, 15, "Enter A Number...")
        self.__set_numberoftweets_button = self.__create_button(190, 40, 750, 300, 'images/set_number_of_tweets.png',
                                                            self.__insert_number_of_tweets_method)

        """" Bottom Frame """

        # Start Button & Status Bar
        self.__start_button = self.__create_button(190, 40, 550, 425, 'images/start.png', self.__start_session)

        # Copyrights Frame
        self.__linkedin_button = self.__create_button(80, 80, 420, 550, 'images/linkedin.png',
                                                      self.__copyrights_btn_links, 'linkedin')
        self.__github_button = self.__create_button(80, 80, 520, 550, 'images/github.png', self.__copyrights_btn_links,
                                                'github')
        self.__gmail_button = self.__create_button(80, 80, 620, 550, 'images/gmail.png', self.__copyrights_btn_links,
                                               'gmail')  # width, height, left, top
        self.__facebook_button = self.__create_button(80, 80, 720, 550, 'images/facebook.png', self.__copyrights_btn_links,
                                                  'facebook')  # width, height, left, top
        self.__twitter_button = self.__create_button(80, 80, 820, 550, 'images/twitter.png', self.__copyrights_btn_links,
                                                 'twitter')  # width, height, left, top

        # Display the UI
        try:
            self.show()
        except SystemError as se:
            print("Couldn't display the UI because: {}".format(se))
        except Exception as e:
            print("Couldn't display the UI because: {}".format(e))


def main():
    app = QApplication(sys.argv)
    main_window = App()
    t = TweetAnalyzer(main_window)
    sys.exit(app.exec_())
