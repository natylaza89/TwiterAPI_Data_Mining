import time
from datetime import datetime

from PyQt5.QtCore import (QObject, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QProgressBar)
from PyQt5.QtGui import QIcon
from tweepy import (Cursor, Stream, StreamListener, TweepError, RateLimitError)


class ThreadsClass(QObject):

    """
    ThreadsClass to perform the data extraction via twitter api with threads.

    Attributes:
        twitter_client (API): API instance.
        num_of_tweets (int): Number of tweets to be pulled out.
        tag_list (Dict): Our Hash Tags.
        statusbar_table statusbar_table (QTextBrowser): Status var at the UI to inform the user about the actions.
        instance (App): The main instance of App class.

    Methods:
        __init__(self, twitter_client, num_of_tweets, tag_list, statusbar_table, instance): Class's constructor.
        super().__init__(): QObject Base Class __init__ constructor.
        run(self): A method which called when starting the search's thread and it's performs the actual search.
    """

    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, twitter_client, num_of_tweets, tag_list, statusbar_table, instance):

        super().__init__()
        self.app = instance
        self.twitter_client = twitter_client
        self.num_of_tweets = num_of_tweets
        self.tag_list = tag_list
        self.statusbar_table = statusbar_table
        self.tweet_matrix = list()
        self.status_bar = self.app.get_statusbar_table

    @staticmethod
    def __create_progress_bar(self):

        pb = QProgressBar()
        pb.setGeometry(500, 300, 400, 25)
        pb.setMaximum(100)
        pb.setWindowTitle("Searching Progress Bar")
        pb.setWindowIcon(QIcon('images/icon.ico'))

        return pb

    def run(self):

        """
        Initializing a Stream & Use Search Engine with User's Hashtags.

        Args:
            None.

        Parameters:
            self.app.listener (StreamListener): Initializing & stores StreamListener object.
            self.app.stream (Stream): Initializing & Store Stream object with auth & listener args.
            tweets_list[] (list): Temporary list in order to store specific hashtag's tweets
            self.tweet_matrix (list): list of lists - Storing lists of tweets for each hashtag.
            self.pb (QProgressBar): Progess bar which present the current status of the search.
            self.tag_list (dict): Hashtags list itself for searching tweets.
            temp_value (float): Temporary value for the continuation of the progress bar.
            start (float): current time in seconds.
            clock (str): current time.
            self.signal (pyqtBoundSignal):Emiting the tweets list of lists back to data_and_analasys_to_excel method.

        Returns:
            None
        """

        # Handles Twitter authetification and the connection to Twitter Streaming API
        self.app.listener = StreamListener()
        self.app.stream = Stream(self.app.auth, self.app.listener)

        # Capture the Tweets in a Temporary List
        tweets_list = []

        try:
                # Creating the Progress Bar and present it.
                self.pb = self.__create_progress_bar(self)
                self.pb.show()

                # Temporary value for the continuation of the progress bar
                temp_value = 0

                for hashtag, search_item in zip(self.tag_list, range(1, len(self.tag_list) + 1)):

                    QApplication.processEvents()

                    # Starting time
                    start = time.time()
                    clock = datetime.now().strftime("%H:%M:%S")

                    cursor = Cursor(self.twitter_client.search, q=hashtag, result_type='mixed', tweet_mode='extended',
                                    include_entities=True, lang="en").items(self.num_of_tweets)

                    # Use Cursor to search for hashtag and copy it into a tweets_list
                    for tweet in cursor:

                        QApplication.processEvents()
                        # Capture a list of tweets
                        tweets_list.append(tweet)

                    # Progress Bar Continuation's Configuration
                    time.sleep(0.05)
                    self.pb.setValue(temp_value + 100/len(self.tag_list))
                    temp_value += 100/len(self.tag_list)

                    print("Search #{} took {} from {}".format(search_item, time.time() - start, clock))

                    # Copy to the List of lists which stores all the tweets for each hashtags & clean the temp list
                    self.tweet_matrix.append(tweets_list.copy())
                    tweets_list.clear()

                # Hiding the Progress Bar
                self.pb.close()

                # Emiting the tweets list of lists back to data_and_analasys_to_excel method.
                self.signal.emit(self.tweet_matrix)

        except RateLimitError as limit:
            print('RateLimit Error: {0}'.format(limit))
        except TweepError as error:
            print('Tweepy Error: {0}'.format(error))
        except Exception as e:
            print('Search Error: {0}'.format(e))
