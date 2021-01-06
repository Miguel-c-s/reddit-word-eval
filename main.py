import praw
from pprint import pprint
import json
import local_settings
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet as wn
import re
import sys

#nltk.download('vader_lexicon') # run only first time
#nltk.download('wordnet') # run only first time

gSid = SentimentIntensityAnalyzer()
gNouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
gWordCount = {}
gRounds = 200
gSearchWord = "python"
if len(sys.argv) > 1:
     gSearchWord = sys.argv[1]



def orderAndPrint():
    orderedWords = sorted(gWordCount.items(), key=lambda item: item[1])
    for i in orderedWords:
        print(i[0], i[1])



def isNoun(word):
    return (word in gNouns)

def addWord(word):
    if isNoun(word):
        if word in gWordCount:
            gWordCount[word] += 1
        else:
            gWordCount[word] = 1


def stringSplitter(string):
    return re.findall(r"[^\,\.\:\;\'\!\"\#\$\%\&\/\(\)\=\?\-\_ ]+", string)



def main():

    reddit = praw.Reddit(client_id=local_settings.CLIENT_ID, client_secret=local_settings.CLIENT_SECRET, user_agent=local_settings.USER_AGENT)

    search = reddit.subreddit('all').search(gSearchWord, limit= gRounds)
    sum = 0
    for i, submission in enumerate(search):
        print(f"round: {i} of {gRounds}")
        if submission.score > 5 and re.search(gSearchWord, submission.title, re.IGNORECASE):
            sum += gSid.polarity_scores(submission.title)['compound'] * submission.score
            for word in stringSplitter(submission.title):
                addWord(word)
            submission.comments.replace_more(limit=0)
            nComments = 0
            for comment in submission.comments:
                if nComments > 10:
                    break
                if comment.score > 5 and re.search(gSearchWord, comment.body, re.IGNORECASE):
                    sum += gSid.polarity_scores(comment.body)['compound'] * comment.score
                    for word in stringSplitter(comment.body):
                        addWord(word)


    orderAndPrint()
    print("\nSUM IS: " + str(sum))




main()