# Machine Learning in Finance — Purdue, Fall 2026

Course notebooks for **FIN 43800** (undergraduate) and **FIN 69000-005** (graduate),
Daniels School of Business, Purdue University. Instructor: Andreas Neuhierl.

## Running the notebooks in Google Colab

- **Week 1:** [open in Colab](https://colab.research.google.com/github/aneuhierl/ml-in-finance-fall2026/blob/main/notebooks/w01-foundations.ipynb)
- **Any notebook:** replace `github.com` in its GitHub URL with
  `colab.research.google.com/github`.

You need a personal Google account (Gmail) and a current browser.
Nothing to install. In Colab, choose **File → Save a copy in Drive** and work
in your copy — edits to the original are not saved.

## Data

Course data is **not** in this repository — some of it is copyrighted. The
data files are posted on the course's Brightspace page. Download the file a
notebook needs, then in Colab click the folder icon on the left and drag the
file in. Colab deletes uploaded files when the session ends, so repeat this
each session. See `src/mlfin_data.py` for how the notebooks find the file.

## Learning Python

No prior Python is assumed.

- [ISLP — *An Introduction to Statistical Learning with Python*](https://www.statlearning.com/resources-python) — free PDF, the book this course follows.
- [ISLP labs](https://github.com/intro-stat-learning/ISLP_labs/tree/stable) — runnable chapter by chapter.
- DataCamp, free through Purdue — see the course slides for the track.

## Layout

    notebooks/   one per class meeting
    psets/       problem sets
    src/         mlfin_data.py, the data helper the notebooks import

Solutions are not published here.
