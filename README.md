# Social Influence Study

## 🚀 Quickstart

First, clone this repository:

```bash
git clone https://mikasenghaas/social-influence-study.git
```

Given, that you have [Poetry](https://python-poetry.org/) installed, you can
install the dependencies by running:

```bash
poetry install
```

Then, you can run the simulation by running:

```bash
poetry run python main.py
```

The experiment setup assumes that the script is ran in a time interval of 24
hours, which is scheduled by running the `run.sh` script using `cron`.
To schedule the cron job, run:

```bash
crontab -e
```

and add the following line:

```bash
0 0 * * * /path/to/social-influence-study/run.sh
```

## 📚 Results

The popularity metrics are continuously logged to a CSV file called `results.csv`.


## 📝 License

This project is licensed under the terms of the [MIT license](LICENSE).
