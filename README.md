# F4A
A website to help explain fair machine learning (video demonstration incoming).

# Table of Contents
- [Setup](#setup-instructions) 
- [Roadmap](#roadmap)


# Setup Instructions
(Please note, these instructions are a work in progress. There are parts missing that are vital for F4A to work. Please contact me at arokray@gmail.com if you'd like to deploy this or contribute, I can get you up and running before later versions are deployed.)

# Prerequisites

- Python >= 3.5 (Highly recommended: Anaconda)
- Postgres 13

# Setup
## Stage 1: Prerequisites

Ensure you have Python 3.5 or greater installed
- Recommended: Install Anaconda, it includes almost all the packages necessary for F4A to run.

Download and install Postgres 13
- Set up your username and password
- Load your username/password into the database.ini file

Ensure that your Python 3.5+ install is being used (whether it be globally via PATH variable or activated virtual environment) by opening Python in a command prompt. Ensure the Python version at the top is correct.

## Stage 2: Project Setup

Clone this repository, or download the code into a single folder.

Download and unzip [Tabulator](http://tabulator.info/) v4.9 (older/newer versions may work, but 4.9 certainly works) into the static/ folder.

Modify the database.ini file to match your database's credentials
- Optional: Use environment variables instead of explicitly coding in username and password.

Download data (suggested: [https://uwyomachinelearning.github.io/](https://uwyomachinelearning.github.io/)) and load the CSV files into the "datasets/" folder. 
- Each dataset requires:
    - 1.) The dataset itself (as a CSV file for now)
    - 2.) *n* rows of training index sets, where the number of columns is the number of instances in the training set and each entry is the index of a training sample.
        - e.g. for a 5 sample dataset, with a 60/40 training/testing split and 3 rows of training sample indices:
        ```
        1,2,3
        0,2,4
        0,1,4
        ````
        meaning the internal code will set the testing sample indices as:
        ```
        0,4
        1,3
        2,3
        ```

- Why do this?
    - Static, initially randomly generated, training/testing sets are necessary for two reasons:

        1.) To ensure that different feature/hyperparameter combinations are compared against one another fairly

        2.) To ensure that the results of the algorithm are *static*, so we can load them into/out of the database for faster lookup times. This is very important for more complex algorithms

# Roadmap
Currently, the project is in a stable state and can be deployed locally. Spring 2021 semester begins February 1st, and my master's degree is my first priority currently. That said, I still plan on developing this application and deploying it by the end of May 2021.

The roadmap for this project is tracked through a Notion project here: https://www.notion.so/F4A-645d588e7b194366b05855778bce17ea