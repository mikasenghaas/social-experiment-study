# config.py
import os

BASE_PATH = os.getcwd()
DATA_PATH = os.path.join(BASE_PATH, "results.csv")
LOGGING_PATH = os.path.join(BASE_PATH, "experiment.log")

M = 24 # number of iterations
N = 500 # number of samples per iterations
