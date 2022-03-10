import argparse, re, os, sys
import numpy as np
import openpyxl
import pandas as pd

cwd = os.getcwd()
print( f" working directory: { cwd }" )

def input_files( header_option:str, file_loc:str, file_extn:str, tweet_loc) :
    '''
    Get file 
    '''

    if file_extn in [ "txt", "text", "csv" ] :
        in_file = pd.read_csv( file_loc, header = header_option, delimiter = "\n", index_col = False )
    elif file_extn == "xls" :
        in_file = pd.read_excel( file_loc, header = header_option, index_col = False )
    else :
        in_file = pd.read_excel( tweet_loc, header = header_option, engine = "openpyxl", index_col = False )

    return in_file

def get_file_loc( file_name ) :

    abs_filepath = []
    for root, dir, files in os.walk( cwd ) :
        if file_name in files :
            abs_filepath.append( os.path.join( root, file_name ) )
    
    return abs_filepath[0]

### Extract Mentions, urls amd hashtags
URLPATTERN = r'(https?://\S+)'
def extract_details( raw_df ) :

    raw_df[ 'Raw_Tweets' ] = raw_df[ 'Raw_Tweets'].astype(str)
    raw_df[ 'mentions' ] = raw_df[ 'Raw_Tweets'].str.findall( r'(?<=@)\w+' ).apply( ','.join )
    raw_df[ 'hashtags' ] = raw_df[ 'Raw_Tweets'].str.findall( r'#(\w+)' ).apply( ','.join )
    raw_df[ 'email_id' ] = raw_df[ 'Raw_Tweets'].str.findall( r'#(\S+@\S+)' )
    raw_df[ 'URLs' ] = raw_df.Raw_Tweets.apply( lambda x: re.findall( URLPATTERN, x ) )

    return raw_df

def clean_tweet( raw_txt, pattern ) :

    remve_char = re.findall( pattern, raw_txt )
    for char in remve_char :
        raw_txt = re.sub( char, '', raw_txt)
    
    return raw_txt

def remove_extras( text ) :
    text = re.sub( r'(\\x(.){2})', '', text )
    return text


def main( ):
    parser = argparse.ArgumentParser(
        prog = 'degree_profanity.py',
        description=" The program which detect search words and estimate the degree of profanity of the tweets from twitter.",
        usage = " %(prog)s <tweet_file> <abuse_file> [options]",
        epilog = ""
    )
    parser.add_argument(
        "tweet_file",
        type = str,
        help = "Tweeter file name with extension"
    )
    parser.add_argument(
        "search_wrd_file",
        type = str,
        help = "filename of search (abuse) words with extension"
    )
    parser.add_argument( 
        '-hdr', '--header',
        action = 'store_true', 
        dest = 'header',
        help = 'Should be called only when there is header in the tweet input file'
    )

    for grp in parser._action_groups :
        if grp.title == 'optional arguments' :
            grp.title = 'options'

    args = parser.parse_args()
    
    tweet_filename = args.tweet_file
    search_wrd_filename = args.search_wrd_file
    if args.header == True :
        header = 'infer'
    else :
        header = None

    tweet_loc = get_file_loc( tweet_filename )
    search_wrd_loc = get_file_loc( search_wrd_filename )

    if not os.path.isfile( tweet_loc ) :
        print( "Location of tweet file is incorrect \n Check and try again!" )
    if not os.path.isfile( search_wrd_loc ) :
        print( "Location of search word file is incorrect \n Check and try again!" )
    else :
        if search_wrd_loc.split( os.sep )[ -1 ].split( "." )[ -1 ] not in [ 'txt', 'text'] :
            print( "file with search words must be a text file with txt/text extension \n check and try again!")
            sys.exit()
        else :
            if os.stat(search_wrd_loc).st_size > 0 :
                with open( search_wrd_loc, "r" ) as search_wrds :
                    list_of_wrds = []
                    for line in search_wrds :
                        line = line.strip( "\n" )
                        list_of_wrds.append( line )

        extn = [ "txt", "xls", "csv", "xlsx" ]
        if tweet_loc.split( os.sep )[ -1 ].split( '.' )[ -1 ] not in extn :
            print( f"Tweet file extension is not in allowed extension - {extn}", end = '\n' )
            print( "Check and Try again!" )
            sys.exit( 0 )


        elif os.stat( tweet_loc ).st_size > 0 :
            tweet_file_extn = tweet_loc.split( os.sep )[ -1 ].split( '.' )[ -1 ]
            input_tweet = input_files( header, tweet_loc, tweet_file_extn, tweet_loc )
        
        col_num = input_tweet.shape[ 1 ]
        col_old0 = input_tweet.columns.to_list( )[ 0 ]
        input_tweet = input_tweet.rename( columns = { col_old0 : "Raw_Tweets" } )

        print( " ************ Raw Tweets ************ " )
        print( input_tweet.head(5), end = '\n' )
        print( f" Total number of tweets { input_tweet.shape[ 0 ] } with { input_tweet.shape[ 1 ] } columns")

        input_tweet[ 'Raw_Tweets' ] = input_tweet[ 'Raw_Tweets' ].apply( remove_extras )
        input_tweet[ 'Tweets' ] = np.vectorize(clean_tweet)( input_tweet[ 'Raw_Tweets' ], "@[\w]*" )
        input_tweet = extract_details( input_tweet )

        def search_words( wrd_tweet ) :
            
            tmp_list1 = [ ]
            tmp_list2 = [ ]
            for wrd1 in list_of_wrds :
                if re.search( wrd1, wrd_tweet, re.IGNORECASE) is not None :
                    tmp_list1.append( wrd1 )
                else :
                    pass
            for wrd2 in tmp_list1 :
                if len(wrd2) == 0 :
                    pass
                else :
                    tmp_list2.append( wrd2 )
            
            srch_wrds = ", ".join(tmp_list2)

            return srch_wrds

        input_tweet[ 'Racial_slurs' ] = input_tweet[ 'Tweets' ].apply( search_words )
        input_tweet[ 'Racial_slurs_count' ] = input_tweet[ 'Racial_slurs' ].apply( lambda x: len( re.findall( r'\w+', x) ) )
        input_tweet[ 'Tweet_word_count' ] = input_tweet[ 'Tweets' ].apply( lambda x: len( re.findall( r'\w+', x) ) )
        input_tweet[ 'Degree of Profanity' ] = input_tweet[ 'Racial_slurs_count' ] / input_tweet[ 'Tweet_word_count' ]

        print( input_tweet[ [ 'Tweets', 'Degree of Profanity' ] ] )

        input_tweet.to_csv( "tweet_degree_profanity.csv", index = False )
        print( "Degree of Profanity for Tweets from different user is estimated.", end = '\n' )
        print( "Saved in tweet_degree_profanity.csv file.", end = '\n' )

if __name__ == "__main__" :
    main( )