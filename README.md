# F4A
A website to help explain fair machine learning (video demonstration incoming).

# Setup Instructions
(Please note, these are a work in progress. There are parts missing that are vital for F4A to work. Please contact me at (arokray@gmail.com)[arokray@gmail.com] if you'd like to deploy this or contribute, I can get you up and running before later versions are deployed.

# Prerequisites

Python >= 3.5 (Highly recommended: Anaconda)

Postgres 13

# Setup
## Stage 1

Ensure you have Python 3.5 or greater installed
- Recommended: Install Anaconda, it includes almost all the packages necessary for F4A to run.

Download and install Postgres
- Set up your username and password
- ...

Ensure that your Python 3.5+ install is being used (whether it be globally via PATH variable or activated virtual environment) by opening Python in a command prompt. Ensure the Python version at the top is correct.

## Stage 2

Clone this repository, or download the code into a single folder.

Modify the database.ini file to match your database's credentials
- Optional: Use environment variables instead of explicitly coding in username and password.

Download data (suggested: [https://uwyomachinelearning.github.io/](https://uwyomachinelearning.github.io/)) and load the CSV files into the "datasets/" folder. 
- Each dataset requires:
    - 1.) The dataset itself (as a CSV file for now)
    - 2.) *n* rows of training indices, where the number of columns is the number of instances in the training set
