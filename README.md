# Profanity_task

This program is to full-fill task given in the interview process at Affinity Answers.

## Description

Two files are given as input such as one file contains Twitter tweets by various users and other consists of a list of search words (here, abuse/racial slurs) in the tweets.

The file which contains the twitter tweets from different users should be in one of the following extensions as csv, txt, text, xls and xlsx. Where as the file with search words should be in txt/text extension.

### Dependencies 

The following libraries are need to be installed to run this script.

```notepad
* pandas
* numpy
* openpyxl
```

## Output

An output csv file is saved as **tweet_profanity_analysis.csv** in the same folder. The *.csv* file has 10 fields: raw tweets, tweets, hashtag, mentions, email-id, URLs, racial slurs, Racial_slurs_count, Tweet_word_count and Degree_profanity.

# Usage

The input files, tweet and search words are locaated on the folder as the script.

To get the detailed description of necessary input are given in commmandline are provided by using the helper option as,
```bash
python .\degree_profanity.py -h
```
The helper message printed as,
```notepad
usage: degree_profanity.py <tweet_file> <abuse_file> [options]

The program which detect search words and estimate the degree of profanity of the tweets from twitter.

positional arguments:
  tweet_file       Tweeter file name with extension
  search_wrd_file  filename of search (abuse) words with extension

options:
  -h, --help       show this help message and exit
  -hdr, --header   Should be called only when there is header in the tweet file
```