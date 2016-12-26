import csv
import os
import os.path
import time

from larry import Larry

#Rhymes with sweeper. Collects tweets from everyone in our training dataset, and
#and dumps them into a file. Individual classifiers will use different
#attributes so preserving the entire tweet.

#Get the set of users for whom we need tweets (aka the training set)
def load_training_data():
  X, profile=load_data("train.csv")
  tweets=get_tweets(X)
  with open('tweets_train.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["user","tweet","leaning"])
    for key, value in tweets.items():
      user=key.lower()
      tweet=value
      writer.writerow([user, tweet, profile[user]])

def get_tweets(X, use_screen_name=True):
  user_tweet_dict=dict()
  try:
    for user in X:
      if user not in user_tweet_dict:
        user_tweet_dict[user] = list()
      consolidated_tweets = user_tweet_dict[user]
      print("User is {0}".format(user))
      if use_screen_name:
        chirps=larry.get_tweets_by_screenname(user)
      else:
        chirps=larry.get_tweets_by_userid(user)
      for chirp in chirps:
        if chirp.user.screen_name not in user_tweet_dict:
          user_tweet_dict[chirp.user.screen_name] = list()
          consolidated_tweets = user_tweet_dict[chirp.user.screen_name]
        #Handle retweets and quotes separately as the tweets _might_ get truncated.
        if chirp.retweeted and hasattr(chirp, "retweeted_status"):
          retweet = chirp.retweeted_status
          if retweet.truncated:
            if hasattr(retweet, "retweeted_status"):
              original=retweet.retweeted_status.full_text
          else:
            if hasattr(retweet, "retweeted_status"):
              original=retweet.retweeted_status.text
          if original!=None:
            consolidated_tweets.append(original)
          original=None
        else:
          if chirp.is_quote_status:
            if hasattr(chirp, 'quoted_status'):
              text=chirp.quoted_status["full_text"]
              consolidated_tweets.append(text)
            if hasattr(chirp, 'retweeted_status'):
              if hasattr(chirp.retweeted_status, 'quoted_status'):
                text=chirp.retweeted_status.quoted_status["full_text"]
                consolidated_tweets.append(text)
          #We can handle non-RTs as is.
          else:
            original=chirp.full_text
            consolidated_tweets.append(original)
      if use_screen_name:
        favourites=larry.get_favourites_by_screenname(user)
      else:
        favourites=larry.get_favourites_by_userid(user)
      for favourite in favourites:
        consolidated_tweets.append(favourite.full_text)
      #time.sleep(10) #One way to handle Twitter rate limits.
  except:
    print("Caught an exception while attempting to extract details for" +
        " user {0}".format(user))
    pass
  return {k:v for k,v in user_tweet_dict.items() if v}

def load_test_data():
  X, profile=load_data("test.csv")
  tweets=get_tweets(X)
  with open('tweets_test.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["user","tweet","leaning"])
    for key, value in tweets.items():
      user=key.lower()
      tweet=value
      writer.writerow([user, tweet, profile[user]])

def load_data(file_name):
  #Look up the current directory and build the path to the training data file.
  current_directory=os.path.dirname(os.path.abspath(__file__))
  data_directory=current_directory + "/data/"
  data_file=data_directory + file_name
  if os.path.isfile(data_file):
    with open(data_file, newline='') as csvfile:
      data=csv.reader(csvfile)
      X=list()
      profile=dict()
      for datum in data: #Statisticians will be happy
        X.append(datum[0])
        #Dict of username with political leaning
        profile[datum[0]]=datum[1]
  return X, profile

larry=Larry()
