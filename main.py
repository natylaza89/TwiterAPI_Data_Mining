"""   Imports   """
# Application
from PyQt5.QtWidgets import (QTextBrowser, QMainWindow, QApplication, QLabel, QLineEdit, QPushButton)
from PyQt5.QtGui import (QIcon, QPixmap, QImage, QPalette, QBrush)
from PyQt5.QtCore import (QSize)

# Tweepy
import twitter_credentials
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# Others
import webbrowser
import sys
import numpy as np
import pandas as pd


class TweetAnalyzer:
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def tweets_to_data_frame(self, tweets):

        """  Copy Data to DataFrame in order to export it into Excel File  """

        df = pd.DataFrame(data=[tweet.full_text for tweet in tweets], columns=['tweets'])
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


class App(QMainWindow):

    def __init__(self):

        """    Application Initilization   """

        super().__init__()
        self.title = 'Twitter Data Mining Final Project'
        self.icon = 'images/icon.ico'
        self.left = 50
        self.top = 35
        self.width = 1280
        self.height = 680
        self.num_of_tweets = 0
        self.tag_list = dict()
        self.tweet_matrix = list()
        self.initUI()

    def twitter_client_auth(self):

        """ Client Authentication with Twitter's API """

        try:
            self.auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
            self.auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
            self.twitter_client = API(self.auth)
            assert(self.twitter_client), self.statusbar_table.append("Twitter Client Authentication Has Failed.")
            return self.twitter_client

        except Exception as e:
                self.statusbar_table.append('<center>Authentication Error: {0}'.format(e))


    def stream_tweets(self, hash_tag_list):

        """ Initialize Stream & Use Search Engine with Hashtags """

        # Clean The Status Bar
        self.statusbar_table.clear()

        # Handles Twitter authetification and the connection to Twitter Streaming API
        self.listener = StreamListener()
        self.stream = Stream(self.auth, self.listener)

        # Capture the Tweets in a List
        tweetsList = []

        try:

            for hashtag in hash_tag_list:

                for tweet in Cursor(self.twitter_client.search, q=hashtag, result_type='mixed', tweet_mode='extended', include_entities=True, include_rts=True, lang="en").items(self.num_of_tweets):
                    tweetsList.append(tweet)

                self.tweet_matrix.append(tweetsList.copy())
                tweetsList.clear()

        except Exception as e:
            self.statusbar_table.append('<center>Search Error: {0}'.format(e))

        # Stream Disconnect
        self.stream.disconnect()

        #return self.tweet_matrix

    def start_session(self):

        """   Start Session   """

        # Clean The Status Bar
        self.statusbar_table.clear()

        if self.tag_list and self.num_of_tweets > 0:
            self.statusbar_table.clear()

            try:

                self.twitter_client = self.twitter_client_auth()
                self.tweet_analyzer = TweetAnalyzer()
                self.stream_tweets(self.tag_list)

                if self.tweet_matrix:

                     # Create a Pandas Excel writer using XlsxWriter as the engine.
                      writer = pd.ExcelWriter('tweets.xlsx', engine='xlsxwriter')

                      for item, tag in zip(self.tweet_matrix, self.tag_list):

                           # Creates Data Frame for each hashtag
                           df = self.tweet_analyzer.tweets_to_data_frame(item)

                           # Convert the dataframe to an XlsxWriter Excel object.
                           df.to_excel(writer, sheet_name=tag)

                       # Close the Pandas Excel writer and exit the Excel file.
                      writer.save()

                      self.statusbar_table.append("<center>Excel file was created successfully")

            except Exception as e:
                self.statusbar_table.append("<center>Error has occured: {}".format(e))

        else:
            self.statusbar_table.append("<center>You Didn't Enter Hashtag or Number Of Tweets.")

    def link(self, name):

        """   Copyrights Links   """

        # Clean The Status Bar
        self.statusbar_table.clear()

        link = {'linkedin':'https://www.linkedin.com/in/natylaza89/',
                 'github':'https://github.com/natylaza89',
                 'gmail':'mailto:natylaza89@gmail.com',
                 'facebook':'https://www.facebook.com/naty.laza',
                 'twitter':'https://twitter.com/natylaza89'}

        try:
            webbrowser.open(link[name])

        except Exception as e:
            self.statusbar_table.append("<center>Error has Occurd: {}".format(e))

    def create_button(self, width, height, top, left, image, func, text=None):

        """   Pattern For Create Button   """

        # Sets Button's Size & Position
        btn = QPushButton(self)
        btn.setFixedWidth(width)
        btn.setFixedHeight(height)
        btn.move(top, left)

        #Sets Button's Image
        btn_image = QPixmap(image)
        btn.setIcon(QIcon(btn_image))
        btn.setIconSize(QSize(200, 200))

        """ Attach Function to a Button according to func & text arguments """

        if text:
            btn.clicked.connect(lambda checked: self.link(text))
        else:
            btn.clicked.connect(func)

        return btn

    def create_line(self, width, height, top, left, size, text):

        """   Pattern For Create Line   """

        # Sets Line's Size & Position
        line = QLineEdit(self)
        line.resize(width, height)
        line.move(top, left)

        # Sets Line's Default Text
        line.setPlaceholderText(text)

        # Sets Text's Size
        line.setStyleSheet("font-size: {}px;".format(size))

        return line

    def insert_number_of_tweets_method(self):

        """   Sets the number of tweets to be export for each hastag   """

        # Clean The Status Bar
        self.statusbar_table.clear()

        try:

            # Gets the text from input line
            text = self.numberoftweets_insert_line.text()

            if text.isdigit() and int(text) > 0:

                self.num_of_tweets = int(self.numberoftweets_insert_line.text())
                self.statusbar_table.append("<center>Number Of Tweets Sets to " + str(int(text)) + ".")

            else:
                self.statusbar_table.append("<center>You Entered Wrong Input")

        except Exception as e:
            self.statusbar_table.append("<center>Error has occured: {}".format(e))

    def add_hashtag_method(self):

        """   Add hashtag to the list and allow only unique hashtags   """

        # Clear Hashtag Table & Status Bar
        self.hashtag_table.clear()
        self.statusbar_table.clear()

        try:

            # Gets the text from input line
            text = self.hashtag__line.text()

            if text:

                if text[0] == '#' and len(text) > 1:

                    # Adds the hashtag to the tag list table

                    if self.tag_list.get(text) is None:

                        self.tag_list[text] = text
                        self.statusbar_table.append('<center>{}'.format(text) + ' has been added!')

                    else:
                        self.statusbar_table.append("<center>Couldn't add because of duplicate TAGS!")

                else:
                    self.statusbar_table.append("<center>Couldn't add this tag")

            else:
                self.statusbar_table.append("<center>Couldn't Add this tag because its empty!")

        except Exception as e:
            self.statusbar_table.append("<center>Error has occured: {}".format(e))

        finally:

            """ Updating the Hashtag Table in the UI """

            for tag in self.tag_list:
                self.hashtag_table.append(tag)

    def remove_hashtag_method(self):

        """   Remove hashtag from the list   """

        # Clear Hashtag Table & Status Bar
        self.hashtag_table.clear()
        self.statusbar_table.clear()

        # Gets the text from input line
        text = self.hashtag__line.text()

        try:

            del self.tag_list[text]
            self.statusbar_table.append("<center>{} has been deleted!".format(text))

        except Exception as e:

            if text:
                self.statusbar_table.append("<center>{} doesn't exist, couldn't delete".format(e))
            else:
                self.statusbar_table.append("<center> Empty input, couldn't delete")

        finally:

            # Update Tag List Table
            for item in self.tag_list:
                self.hashtag_table.append(item)


    def initUI(self):

        """Main Window Configurtaion"""

        self.setWindowIcon(QIcon(self.icon))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        """"Window Background Image"""

        bg_image = QImage("images/background.png")
        bg_image = bg_image.scaled(QSize(1500, 1024))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(bg_image))  # 10 = Windowrole
        self.setPalette(palette)

        """"Banner\Logo"""

        self.label = QLabel(self)
        pixmap = QPixmap('images/banner.png')
        pixmap = pixmap.scaled(QSize(900, 150))
        self.label.setPixmap(pixmap)
        self.label.setGeometry(200, 20, 900, 150)

        """"Top Frame"""

        """ Left Side"""
        self.hashtag_table = QTextBrowser(self)
        self.hashtag_table.setGeometry(175, 200, 350, 200)
        self.hashtag_table.setStyleSheet("font-size: 15px;")

        """ Center & Right Side """
        #Hashtag Handler
        self.hashtag__line = self.create_line(200, 40, 540, 200, 15, "Enter #hashtag...")
        self.add_hashtag_button = self.create_button(190, 40, 750, 200,'images/add_hashtag.png', self.add_hashtag_method)
        self.remove__hashtag_button = self.create_button(190, 40, 950, 200, 'images/remove_hashtag.png', self.remove_hashtag_method)

        # Number Of Tweets Insert Line
        self.numberoftweets_insert_line = self.create_line(200, 40, 540, 250, 15, "Enter A Number...")
        self.set_numberoftweets_button = self.create_button(190, 40, 750, 250, 'images/set_number_of_tweets.png', self.insert_number_of_tweets_method)

        """"Bottom Frame"""

        self.start_button = self.create_button(190, 40, 550, 425, 'images/start.png', self.start_session)

        self.statusbar_table = QTextBrowser(self)
        self.statusbar_table.setGeometry(250, 485, 800, 50)
        self.statusbar_table.setStyleSheet("font-size: 30px;")

        """"Copyrights Frame"""

        self.linkedin_button = self.create_button(80, 80, 420, 550, 'images/linkedin.png', self.link, 'linkedin')  # width, height, left, top
        self.github_button = self.create_button(80, 80, 520, 550, 'images/github.png',  self.link, 'github')  # width, height, left, top
        self.gmail_button = self.create_button(80, 80, 620, 550, 'images/gmail.png', self.link, 'gmail')  # width, height, left, top
        self.facebook_button = self.create_button(80, 80, 720, 550, 'images/facebook.png',  self.link, 'facebook')  # width, height, left, top
        self.twitter_button = self.create_button(80, 80, 820, 550, 'images/twitter.png',  self.link, 'twitter')  # width, height, left, top

        self.show()


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())