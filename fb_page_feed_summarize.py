import facebook
import requests, requests.exceptions
from datetime import datetime
import logging
import time
import csv


def retry(retry_limit, sleep, func, *args, **kwargs):
    """Keeps retrying a function @func with the given arguments. Waits for @sleep seconds
    between attempts and makes a maximum of @limit attempts, unless it is False in which case
    retries forever."""
    attempts = 0
    while attempts < retry_limit if retry_limit else True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error('Exception occurred in attempt {}. Error message: {}. Retrying...'.format(attempts+1, e))
            if sleep > 0:
                time.sleep(sleep)
        attempts += 1
    raise RuntimeError('Failed after {} attempts.'.format(attempts))


class FBPost:
    def __str__(self):
        format_str = 'FBPost:\n id = {id}\n type = {type}\n created time = {ct:%H:%M:%S%z}\n message len = {msglen}\n' \
            ' shares count = {shares}\n likes count = {likes}\n comments count = {comments}\n'
        return format_str.format(id=self.id, type=self.type, msglen=self.message_length, ct=self.time,
                                 shares=self.shares_count,likes=self.likes_count, comments=self.comments_count)

class FBPageFeed:
    FIELDS = 'message,type,created_time,likes.limit(1).summary(true),shares,comments.limit(1).summary(true)'

    def __init__(self, profile_name):
        app_id = "1684491445125602"
        app_secret = "19fb0dd144a3e5a74746d973a77f8817"
        graph = facebook.GraphAPI(version='2.5', timeout=5)
        graph.access_token = retry(20, 5, graph.get_app_access_token, app_id, app_secret)
        self.profile = retry(20, 5, graph.get_object, profile_name)
        self.graph = graph

    def retrieve_posts(self, since, until):
        """@since and @until are Unix timestamps"""
        posts = retry(20, 5, self.graph.get_connections, self.profile['id'], 'posts', since=since,
                      limit=100, until=until, fields=FBPageFeed.FIELDS)
        while True:
            for post in posts['data']:
                yield self.create_from_graph_post(post)
            try:
                # Attempt to make a request to the next page of data, if it exists.
                time.sleep(.5)
                #posts = requests.get(posts['paging']['next'], timeout=5).json()
                posts = retry(20, 5, requests.get, posts['paging']['next'], timeout=5).json()
            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break

    def create_from_graph_post(self, post):
        """Creates an instance of FBPost from the @post object which is a node on FB graph API"""
        # set properties
        #logger.debug(post)
        fb_post = FBPost()
        fb_post.id = post['id']
        fb_post.type = post['type']
        post_datetime = datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z')
        fb_post.date = post_datetime.date()
        fb_post.time = post_datetime.time()
        if 'message' in post:
            fb_post.message_length = len(post['message'])
        else:
            fb_post.message_length = 0
        if 'shares' in post:
            fb_post.shares_count = post['shares']['count']
        else:
            fb_post.shares_count = 0
        if 'likes' in post:
            fb_post.likes_count = post['likes']['summary']['total_count']
        else:
            fb_post.likes_count = 0
        if 'comments' in post:
            fb_post.comments_count = post['comments']['summary']['total_count']
        else:
            fb_post.comments_count = 0
        return fb_post

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    page_id = 'bbcnews'
    feed = FBPageFeed(page_id)
    since = datetime(2010, 1, 1).timestamp()
    until = datetime(2016, 1, 1).timestamp()

    csv_file = page_id + '.csv'
    with open(csv_file, 'w', newline='') as f:
        csv_w = csv.writer(f)
        csv_w.writerow(['id', 'type', 'date', 'time', 'message_length', 'shares_count', 'likes_count',
                        'comments_count'])
        for post in feed.retrieve_posts(since, until):
            print(post.date)
            row = [post.id, post.type, post.date, post.time, post.message_length, post.shares_count,
                   post.likes_count, post.comments_count]
            csv_w.writerow(row)
