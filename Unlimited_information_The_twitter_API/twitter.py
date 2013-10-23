"""Code to fetch information from twitter. Blogpsot: <insert URL>

Ran in background, gathers information from twitter using the user credentials
and upload each twitter to a CouchDB instance.
"""

import ConfigParser
import os
import twitter
import couchdb

def get_config():
    """Return an object ConfigParser.
    """
    conf_file = os.path.join(os.environ['HOME'], '.pytwitterrc')

    if not os.path.exists(conf_file):
        raise RuntimeError('~/.pytwitterrc configuration file not found!')
    else:
        conf = ConfigParser.ConfigParser()
        conf.read(conf_file)
        return conf


def load_twitter_credentials():
    """Return twitter credentials read from ~/.pytwitterrc
    """
    conf = get_config()
    try:
        credentials = dict(conf.items('API'))
        access_key = credentials.get('access_key', False)
        access_secret = credentials.get('access_secret', False)
        customer_key = credentials.get('customer_key', False)
        customer_secret = credentials.get('customer_secret', False)
    except ConfigParser.NoSectionError:
        raise RuntimeError('There is no [API] section in your config file.')

    if not all([access_key, access_secret, customer_key, customer_secret]):
        raise RuntimeError('Your configuration file appears to be incomplete.')

    return credentials


def load_couchdb_credentials():
    """Return couchdb credentials read from .pytwitterrc
    """
    conf = get_config()
    try:
        credentials = dict(conf.items('couchdb'))
        db = credentials.get('database', False)
        port = credentials.get('port', False)
        user = credentials.get('user', False)
        password = credentials.get('password', False)
    except ConfigParser.NoSectionError:
        raise RuntimeError('There is no [couchdb] section in your config file.')

    if not all([db, port, user, password]):
        raise RuntimeError('Your configuration file appears to be incomplete.')

    return credentials


#Create an OAuth object and an instance of Twitter API
credentials = load_twitter_credentials()
auth = twitter.oauth.OAuth(credentials.get('access_key'),
                           credentials.get('access_secret'),
                           credentials.get('customer_key'),
                           credentials.get('customer_secret'))

twitter_api = twitter.Twitter(auth=auth)

#Create a connection to couchDB, where we will store the tweets
credentials = load_couchdb_credentials()
couch = couchdb.Server("{database}:{port}/".format(
                                        database = credentials.get('database'),
                                        port = credentials.get('port')))
couch.resource.credentials = (credentials.get('user'), credentials.get('password'))
tweets_db = couch['tweets']

#XXX: Parse arguments to let the user decide the interval time for polling and the
#duration of it (i.e poll every minute during 1h/1d/1w)
