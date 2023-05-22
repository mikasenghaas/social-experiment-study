# utils.py
import logging
from datetime import datetime

import praw
import pandas as pd

from config import LOGGING_PATH


def get_logger(name):
    """
    Get logger

    Returns:
        logging.Logger: logger
    """
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOGGING_PATH)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    fmt = "%(asctime)s - %(levelname)s - %(message)s"
    c_format = logging.Formatter(fmt)
    f_format = logging.Formatter(fmt)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


def reddit_login(client_id, client_secret, username, password, user_agent):
    """
    Login to Reddit API

    Args:
        client_id (str): client id
        client_secret (str): client secret
        username (str): username
        password (str): password
        user_agent (str): user agent

    Returns:
        praw.Reddit: reddit api object
    """
    # reddit api login
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent,
    )
    return reddit


def extract_submission_meta(sub: praw.models.Submission) -> dict:
    """
    Extract submission metadata

    Args:
        sub (praw.models.Submission): submission objects

    Returns:
        dict: Dictionary of submission metadata
    """
    date_time = datetime.fromtimestamp(sub.created_utc).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "id": sub.id,
        "title": sub.title,
        "datetime": date_time,
        "subreddit": sub.subreddit.display_name,
        "url": sub.url,
        "score": sub.score,
        "ups": sub.ups,
        "downs": sub.downs,
        "num_comments": sub.num_comments,
    }


def submissions_to_df(reddit_posts, new=False):
    """
    Add new extracted reddit posts to dataframe

    Args:
        reddit_posts (list[dict]): list of dicts of extracted metadata from reddit posts
        new (bool, optional): whether the posts are new or not. Defaults to False.
    """
    # create df from list of strings and set index col to id
    column_order = [
        "id",
        "iteration"
        "datetime",
        "title",
        "score",
        "ups",
        "downs",
        "num_comments",
        "treatment",
        "subreddit",
        "url",
    ]

    # create df of new reddit posts
    df = pd.DataFrame(reddit_posts)

    # add column of ones for iteration
    if new:
        df["iteration"] = 1

    # reorder columns
    df = df[column_order]

    return df.set_index(keys=["id", "iteration"])


def read_csv(filename: str) -> pd.DataFrame:
    """
    Read csv file

    Args:
        filename (str): filename

    Returns:
        pd.DataFrame: dataframe
    """
    try:
        return pd.read_csv(filename, index_col=["id", "iteration"])
    except FileNotFoundError:
        return None


def write_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Write dataframe to csv

    Args:
        df (pd.DataFrame): dataframe
        filename (str): filename
    """
    df.to_csv(filename)
