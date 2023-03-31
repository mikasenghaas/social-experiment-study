# Social Influence Study

## 🚀 Quickstart

First, clone this repository:

```bash
git clone https://mikasenghaas/social-influence-study.git
```

Given, that you have [Poetry](https://python-poetry.org/) and Python `3.10.X`
installed, you can install the project dependencies by running:

```bash
poetry install
```

This project uses `praw` to interact with the Reddit API. To use the Reddit API,
you need to create a Reddit account and register an app. For more information,
see [here](https://praw.readthedocs.io/en/latest/getting_started/authentication.html).

Save your client ID, client secret, and user agent in a file called
`.env` in the root directory of the project. The file should look like this:

```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USERNAME=your_username
PASSWORD=your_password
USER_AGENT=your_user_agent
```

Then, you can initiate a single run of the experiment by running:

```bash
poetry run python main.py
```

The experiment setup assumes that the main script runs in a time interval of 24
hours, which is scheduled by running the `run.sh` script using `cron`.
To schedule the cron job, run:

```bash
crontab -e
```

and add the following line:

```bash
0 0 * * * /path/to/social-influence-study/run.sh
```

## 📚 Outputs

The popularity metrics for the Reddit posts are continuously written to a CSV
file called `results.csv`.

The experiment creates logs in the file `experiment.log` to oversee the progress of
the experiment over time and to debug potential issues.

## 📝 License

This project is licensed under the terms of the [MIT license](LICENSE).
