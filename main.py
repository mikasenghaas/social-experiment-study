# main script
import os
from dotenv import load_dotenv
import pandas as pd

from utils import (
    get_logger,
    reddit_login,
    get_random_submissions,
    extract_submission_meta,
    submissions_to_df,
    read_csv,
    write_csv,
)
from config import DATA_PATH, N


def main():
    # get loggin object
    logger = get_logger(__name__)

    # load environment variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    useragent = os.getenv("USERAGENT")
    logger.info("[DONE] Loading environment variables")

    reddit = reddit_login(client_id, client_secret, username, password, useragent)

    # get new batch of reddit posts
    new_submissions = []
    for sub in reddit.subreddit("all").stream.submissions():
        if sub.num_comments == 0 and sub.score == 1 and not sub.over_18:
            new_submissions.append(sub)
            logger.info(f"Loading Submission '{sub.id}'")

        if len(new_submissions) == N:
            break

    # upvote the first half of the batch
    extracted_posts = []
    for i, submission in enumerate(new_submissions):
        # extract metadata
        submission_meta: dict = extract_submission_meta(submission)

        # log extracted submission
        logger.info(
            f"Extracted Submission '{submission_meta['id']}' "
            f"from '{submission_meta['subreddit']}'"
        )

        # upvote the submission
        if i < N // 2:
            try:
                submission.upvote()
            except Exception:
                logger.warning(f"Could not upvote submission '{submission_meta['id']}'")
            submission_meta.update({"treatment": 1})
        else:
            submission_meta.update({"treatment": 0})

        extracted_posts.append(submission_meta)

    new_submissions_df = submissions_to_df(extracted_posts, new=True)
    logger.info("[DONE] Extracting new submissions")

    # load previous batch of reddit posts
    previous_submissions_df = read_csv("data.csv")
    if previous_submissions_df is None:
        write_csv(new_submissions_df, DATA_PATH)
        logger.info("No previous days found. Initializing CSV with new submissions")
        logger.info("[DONE] Run")
        return

    logger.info("[DONE] Loading previous submissions")

    # filter out posts that have been tracked for more than 7 days
    submissions_to_track = (
        previous_submissions_df.reset_index().groupby(["id", "treatment"]).max("day")
    )
    submissions_to_track = submissions_to_track[submissions_to_track["day"] < 7]
    submissions_to_track = submissions_to_track.reset_index()
    submissions_to_track = submissions_to_track[["id", "day", "treatment"]]

    # convert to list of tuples
    submission_to_track = submissions_to_track.to_records(index=False)
    logger.info("[DONE] Filtering out submissions to track")

    # track popularity metrics for all posts
    tracked_submissions = []
    for i, (sub_id, day, treatment) in enumerate(submission_to_track):
        submission = reddit.submission(id=sub_id)
        submission_meta = extract_submission_meta(submission)
        submission_meta.update({"day": day + 1, "treatment": treatment})
        logger.info(
            f"Tracking Submission '{submission_meta['id']}' "
            f"on Day {submission_meta['day']}"
        )
        tracked_submissions.append(submission_meta)
    tracked_submissions_df = submissions_to_df(tracked_submissions, new=False)

    # combine new and tracked submissions
    df = pd.concat(
        [previous_submissions_df, new_submissions_df, tracked_submissions_df]
    )
    logger.info("[DONE] Combining previous, new and tracked submissions")

    write_csv(df, DATA_PATH)
    logger.info("[DONE] Run")


if __name__ == "__main__":
    main()
