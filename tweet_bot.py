from keys import *
import tweepy
import requests
import json
import random
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import RegexpTokenizer
from nltk import pos_tag
import sys

stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
tokenizer = RegexpTokenizer('[A-Za-z]\w+')


# TODO natural language processing to find good hash tags

videogame_tags = " #video #videogame #videogames #gaming #news #videogamenews "
animemanga_tags = " #anime #manga #animenews #manganews #news "
sciencetech_tags = " #science #tech #technology #news #technews #technologynews #sciencenews "

def getArticle(type):
    if type == 0:
        url = ('https://newsapi.org/v2/top-headlines?'
               'sources=ign,polygon&'
               'apiKey=983d2e5d72de4c39be316b926057f008')
    elif type == 1:
        url = ('https://newsapi.org/v2/top-headlines?'
               'sources=ars-technica,techcrunch,recode,wired&'
               'apiKey=983d2e5d72de4c39be316b926057f008')
    else:
        url = ('https://newsapi.org/v2/top-headlines?'
               'sources=national-geographic,new-scientist,next-big-future&'
               'apiKey=983d2e5d72de4c39be316b926057f008')

    response = requests.get(url)
    r = json.loads(response.text)
    num_responses = len(r['articles'])
    article_index = random.randint(0,num_responses-1)
    url = r['articles'][article_index]['url']
    image_url = r['articles'][article_index]['urlToImage']
    title = r['articles'][article_index]['title']
    word_tokens = tokenizer.tokenize(title)
    print pos_tag(word_tokens)
    lemmatized_words = []
    for word in word_tokens:
        lword = lemmatizer.lemmatize(word)
        if lword.lower() not in stop_words:
            lemmatized_words.append(lword)
    print 'article title: ' + title
    print 'tokenized words: ' + str(word_tokens)
    print 'lemmatized words: ' + str(lemmatized_words)
    print 'url len: ' + str(len(url))
    print url
    return url, lemmatized_words
    # for item in r['articles']:
    #     print item['url']
    #     print item['urlToImage']

def twitter_auth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api


def tweet(text, image=None):
    api = twitter_auth()
    # api.update_status(image,text)
    api.update_status(text)

def search(term):
    api = twitter_auth()

    result = api.search(term)
    print result[0].text
    return result[0].id, api

def retweet_search(result, api):
    api.retweet(result)

def random_retweet():
    seed = random.randint(0,100)
    if seed <= 75:
        search_result, api = search('video game news')
    else:
        search_result, api = search('anime manga news')
    retweet_search(search_result, api)

def random_tweet():
    seed = random.randint(0, 100)
    if seed <= 50:
        type = 0
    elif seed > 50 and seed <= 80:
        type = 1
    else:
        type = 2
    article = getArticle(type)
    smart_tags = article[1]
    text_to_tweet = article[0]
    for word in smart_tags:
        text_to_tweet += ' #' + word
    if type == 0:
        text_to_tweet += videogame_tags
    elif type == 1:
        if 'anime' in text_to_tweet or 'manga' in text_to_tweet:
            text_to_tweet += animemanga_tags
    else:
        text_to_tweet += sciencetech_tags
    text_to_tweet += 'powered by NewsAPI'
    print 'final tweet: ' + text_to_tweet
    tweet(text_to_tweet)


# main methods
# random_tweet()
#random_retweet()
command = sys.argv[1]
try:
    if command == '0':
        random_tweet()
        # print 'tweet'
    elif command == '1':
        random_retweet()
        # print 'retweet'
    else:
        raise Exception('error tweeting')
except:
    with open('error_log.txt', 'w') as outFile:
        outFile.write('there was an error tweeting command code: ' + command + ' \n')


# other stuff
def track_twitter_stream(phrase_to_track):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # api = tweepy.API(auth)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5,
                     retry_errors=5)

    streamListener = TwitterStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=streamListener)

    myStream.filter(track=[phrase_to_track], async=True)

class TwitterStreamListener(tweepy.StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def on_status(self, status):
        # get_tweet(status)
        print status.user.name
        print status.text

    # Twitter error list : https://dev.twitter.com/overview/api/response-codes

    def on_error(self, status_code):
        if status_code == 403:
            print("The request is understood, but it has been refused or access is not allowed. Limit is maybe reached")
            return False
