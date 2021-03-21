"""All functions and classes using the Twitter API

This file is Copyright (c) 2020 Mark Bedaywi
"""
import doctest
import random
from datetime import datetime
from typing import List, Set, Tuple
from dataclasses import dataclass

import python_ta
import twython

# Authentication given from Twitter
APP_KEY = ...
APP_SECRET = ...

DENYING_HASHTAGS = {
    "climatechangehoax",
    "globalwarminghoax",
    "climatedeniers",
    "climatechangeisfalse",
    "climatechangenotreal"
}
NON_DENYING_HASHTAGS = {
    "actonclimate",
    "climateaction",
    "climatechangeisreal",
    "globalwarmingisreal"
}
DENYING_WORDS = {
    "hoax",
    "not real",
    "debunk",
    "fake",
    "conspiracy"
}
NON_DENYING_WORDS = {
    "not a hoax",
    "quick",
    "real",
    "act"
}


@dataclass
class Tweet:
    """Stores Tweet Data

    Instance Attributes:
        - text: The text contained in the tweet
        - hashtags: The hashtags contained in the tweet
        - date: The date the tweet was published
        - location: The reported location by the user publishing the tweet
        - user: The username of the user publishing the tweet
    """
    text: str
    hashtags: Set[str]
    date: datetime
    location: str
    user: str


class TweetAnalyser:
    """Infers interesting information from Tweets"""

    @staticmethod
    def tweet_denial_rating(tweet: Tweet) -> float:
        """Returns a tweet denial rating, an ad hoc rating of the
        how strongly the tweet denies climate change from a scale of -1 to 1

        The larger the rating, the more climate change is denied

        Fails on sarcasm

        This is inspired by Q3 in assignment 3
        """
        denying_words_score = 0
        denying_hashtags_score = 0
        total_words = 0
        total_hashtags = 0

        for denying_word in DENYING_WORDS:
            if denying_word in tweet.text:
                denying_words_score += 1
                total_words += 1
        for non_denying_word in NON_DENYING_WORDS:
            if non_denying_word in tweet.text:
                denying_words_score -= 1
                total_words += 1
        for denying_hashtag in DENYING_HASHTAGS:
            if denying_hashtag in tweet.hashtags:
                denying_hashtags_score += 1
                total_hashtags += 1
        for non_denying_hashtag in NON_DENYING_HASHTAGS:
            if non_denying_hashtag in tweet.hashtags:
                denying_hashtags_score -= 1
                total_hashtags += 1

        if total_words + total_hashtags == 0:
            return 0

        score = (denying_hashtags_score + denying_words_score) \
            / (total_words + total_hashtags)

        return score

    @staticmethod
    def common_times(tweets: List[Tweet]) -> List[datetime]:
        """Returns the ten most common days that a climate change tweet occured.

        Since tweets from 7 days ago were manually added, they will not be considered

        The results will be manually compared to world events related to climate
        change at the time.
        """
        # counts the tweets per day
        dates = {}
        for tweet in tweets:
            if tweet.date.year == 2020:
                continue
            if tweet.date.date() in dates:
                dates[tweet.date.date()] += 1
            else:
                dates[tweet.date.date()] = 1

        print(dates)

        # finds the 10 most common days
        top10 = [(None, 0) for _ in range(10)]
        for date in dates:
            for i in range(10):
                if top10[i][1] < dates[date]:
                    top10.insert(i, (date, dates[date]))
                    top10 = top10[:10]
                    break
        return top10

    @staticmethod
    def location_score(tweets: List[Tweet], location: str, is_code: bool) \
            -> Tuple[float, int]:
        """Returns the amount of denial of tweets and the number of tweets in a certain location.

        is_code takes into account that the code of a location has to be upper case

        Will not be completely accurate as some twitter users do not report their location."""

        total = 0
        amount = 0
        for tweet in tweets:
            if is_code:
                if location in tweet.location:
                    total += TweetAnalyser.tweet_denial_rating(tweet)
                    amount += 1
            else:
                if location in tweet.location.lower():
                    total += TweetAnalyser.tweet_denial_rating(tweet)
                    amount += 1

        return (total, amount)


class Twitter:
    """Holds all functions that are needed to create the tweet data set

    Instance Attributes:
        - twitter: Holds the Twython object used
        - ids: Holds all the ids gathered
        - ids_seen: Holds all the ids already seen, to store in a file so that
            when the file is updated again duplicates will not occur
    """
    twitter: twython.Twython
    ids: List[str]
    ids_seen: List[str]

    def __init__(self) -> None:
        """Initialise the Twython object"""
        self.twitter = twython.Twython(APP_KEY, APP_SECRET)
        self.ids = self.get_tweet_ids()
        self.ids_seen = []

    def get_tweet_ids(self) -> List[str]:
        """Return a list of tweet ids collected from the data set"""
        f0 = open("data/climate_id.txt.00")
        f1 = open("data/climate_id.txt.01")
        f2 = open("data/climate_id.txt.02")
        f3 = open("data/climate_id.txt.03")

        # strip is used to remove the newline at the end of each id
        ids = {line.strip() for line in f0.readlines()}
        ids.union({line.strip() for line in f1.readlines()})
        ids.union({line.strip() for line in f2.readlines()})
        ids.union({line.strip() for line in f3.readlines()})

        f0.close()
        f1.close()
        f2.close()
        f3.close()

        # remove ids already in the data set
        f = open("data/Ids_Seen.txt", "r")
        already_seen = {line.strip() for line in f.readlines()}
        for tweet_id in already_seen:
            ids.remove(tweet_id)

        f.close()

        return list(ids)

    def get_tweets_from_ids(self, tweet_ids: List[str]) -> List[dict]:
        """Return a list of tweets from a list of tweet ids

        Used to create the modified data set
        """
        return self.twitter.lookup_status(id=tweet_ids, tweet_mode='extended')

    def get_tweets_from_hashtag(self, hashtag: str, max_id: str = None) -> List[dict]:
        """Search for tweets containing a certain hashtag

        Used to create the modified data set"""
        if max_id is not None:  # get an older search
            return self.twitter.search(
                q="#" + hashtag,
                count=100,
                tweet_mode='extended',
                max_id=max_id
            )['statuses']
        else:
            return self.twitter.search(
                q="#" + hashtag,
                count=100,
                tweet_mode='extended'
            )['statuses']

    def get_tweets(self, amount: int) -> List[dict]:
        """Generates tweets from the Harvard database of tweet ids

        Used to create the modified data set

        parameters:
            - amount: amount of tweets returned
        """
        tweets = []
        while len(tweets) < amount:
            tweet_ids = []

            # The twitter API only allows up to 100 tweets per search
            for _ in range(min(amount - len(tweets), 100)):
                pick = random.randint(0, len(self.ids) - 1)
                tweet_id = self.ids.pop(pick)
                tweet_ids.append(tweet_id)

                # adds the tweet to the already seen file, so that
                # it will not be put in Climate_Tweets.txt twice
                self.ids_seen.append(tweet_id)

            tweet = self.get_tweets_from_ids(tweet_ids)
            tweets.extend(tweet)

        return tweets

    def get_denying_tweets(self) -> List[dict]:
        """Finds Tweets with denying hashtags
        as the harvard dataset does not contain enough of them
        to be able to make interesting conclusions

        The search can only find 100 tweets per query that are 7 days old at most"""
        tweets = []
        for hashtag in DENYING_HASHTAGS:
            hashtag_tweets = self.get_tweets_from_hashtag(hashtag)
            if len(hashtag_tweets) == 0:  # no tweets found with this hashtag
                continue
            for _ in range(10):
                max_id = str(min([int(tweet["id"]) for tweet in hashtag_tweets]))
                hashtag_tweets.extend(self.get_tweets_from_hashtag(hashtag, max_id=max_id))
            tweets.extend(hashtag_tweets)

        return tweets

    def create_tweet_dataset(self, amount: int) -> None:
        """Creates the dataset of tweets, stores this as a JSON file

        For extra flexibility, this is stored as a json string as is from
        Twitter in the file, then is turned into a Tweet object when processing later

        Creates a new file

        parameters:
            - amount: the amount of tweets added to the file Climate_Tweets.txt
        """
        f = open("data/Climate_Tweets.txt", "a", encoding="utf-8")
        g = open("data/Ids_Seen.txt", "a")
        tweets = self.get_tweets(amount)
        for tweet in tweets:
            f.write(str(tweet) + '\n')

        for id_seen in self.ids_seen:
            g.write(id_seen + '\n')

        self.ids_seen = []

        f.close()
        g.close()


if __name__ == "__main__":
    python_ta.check_all()
    doctest.testmod()
