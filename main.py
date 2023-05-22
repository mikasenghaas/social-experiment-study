# main script
import os
from dotenv import load_dotenv
import pandas as pd

from utils import (
    get_logger,
    reddit_login,
    extract_submission_meta,
    submissions_to_df,
    read_csv,
    write_csv,
)
from config import DATA_PATH, M, N


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

    # login to reddit
    reddit = reddit_login(client_id, client_secret, username, password, useragent)
    logger.info("[DONE] Logging into Reddit")

    # load new submissions from r/all
    new_submissions: list[dict] = []
    for sub in reddit.subreddit("all").stream.submissions():
        # only consider adequate submissions with no comments and score of 1
        if sub.num_comments == 0 and sub.score == 1 and not sub.over_18:
            try:
                # extract submission meta data
                sub_meta: dict = extract_submission_meta(sub)
            except Exception:
                logger.warning(f"Could not extract Submission '{sub.id}'. Disregarding")
                continue
            logger.info(f"Extracted Submission '{sub_meta['id']}'")

            if len(new_submissions) < N // 2:
                try:
                    # try to upvote submission
                    sub.upvote()
                    sub_meta.update({"treatment": 1})
                except Exception as e:
                    logger.warning(
                        f"Could not upvote ({e}). Disregarding '{sub_meta['id']}'"
                    )

                    continue
            else:
                sub_meta.update({"treatment": 0})

            # append to list of new submissions
            new_submissions.append(sub_meta)

        if len(new_submissions) == N:
            break

    new_submissions_df = submissions_to_df(new_submissions, new=True)
    logger.info("[DONE] Extracting new submissions")

    # load previous batch of reddit posts
    previous_submissions_df = read_csv(DATA_PATH)
    if previous_submissions_df is None:
        write_csv(new_submissions_df, DATA_PATH)
        logger.info("No previous iter found. Initializing CSV with new submissions")
        logger.info("[DONE] Run")
        return

    logger.info("[DONE] Loading previous submissions")

    # filter out posts that have been tracked for more than M
    submissions_to_track = (
        previous_submissions_df.reset_index()
        .groupby(["id", "treatment"])
        .max("iteration")
    )
    submissions_to_track = submissions_to_track[
        submissions_to_track["iteration"] < M
    ]
    submissions_to_track = submissions_to_track.reset_index()
    submissions_to_track = submissions_to_track[["id", "iteration", "treatment"]]

    # convert to list of tuples
    submission_to_track = submissions_to_track.to_records(index=False)
    logger.info("[DONE] Filtering out submissions to track")

    # track popularity metrics for all posts
    tracked_submissions = []
    for i, (sub_id, iteration, treatment) in enumerate(submission_to_track):
        try:
            # get submission object with specified id
            sub = reddit.submission(id=sub_id)

            # extract submission meta data
            sub_meta = extract_submission_meta(sub)
        except Exception:
            logger.warning(f"Could not extract Submission '{sub_id}'. Disregarding")
            continue

        sub_meta.update({"iteration": iteration + 1, "treatment": treatment})
        logger.info(
            f"Tracking Submission '{sub_meta['id']}' " f" ({sub_meta['iteration']})"
        )
        tracked_submissions.append(sub_meta)
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
