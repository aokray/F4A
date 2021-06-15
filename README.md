<p align='center'>
    <img src='static/f4a_logo.png' alt='F4A Logo' width='250'/>
</p>

# F4A
A website to help explain fair machine learning (video demonstration incoming).

# Table of Contents
- [Setup](#setup-instructions) 
- [Roadmap](#roadmap)


# Setup Instructions
(Please note, these instructions are a work in progress.)

# Prerequisites

- Python >= 3.5 (Highly recommended: Anaconda)
- Postgres 13

# Setup
## Stage 1: Prerequisites

Ensure you have Python 3.5 or greater installed
- Recommended: Install Anaconda, it includes almost all the packages necessary for F4A to run.
- Optional between step, set up a virtual environment
- Install Flask, version ~1.1.2 (versions newer or older probably work fine)

Download and install Postgres 13
- Set up your username and password
- Load your username/password into the database.ini file
- ...

Ensure that your Python 3.5+ install is being used (whether it be globally via PATH variable or activated virtual environment) by opening Python in a command prompt. Ensure the Python version at the top is correct.

## Stage 2: Project Setup

1.) Clone this repository, or download the code into a single folder.

2.) Download necessary packages for frontend and put them into the "static/" folder.
 - [Tabulator](http://tabulator.info/) v4.9 (older/newer versions may work, but 4.9 certainly works)
 - [Tooltipster](https://github.com/calebjacob/tooltipster) master branch


3.) Modify the database.ini file to match your database's credentials

4.) Download data (suggested/see for a template of data format: [http://okray.ml/data](http://okray.ml/data)) and load the CSV files into the "datasets/" folder (currently coded in: Credit Default dataset). 
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


5.) Set up the database
- Open the db_init folder and run the "create.sql" file. This will make the necessary database tables.
- Optional: Run the "load.sql" file to load in the Credit Default data set example

# Roadmap
Currently, the project is in a stable state and can be deployed locally.
The roadmap for this project is tracked through a Notion project here: https://www.notion.so/F4A-645d588e7b194366b05855778bce17ea