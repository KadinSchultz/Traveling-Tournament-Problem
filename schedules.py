from config import teams, games, rounds, df_distMatrix, teamList

import numpy as np
import pandas as pd
import re
from random import randrange

# Check that there are not more than three consecutive home/away games in a schedule
def homeAwayCheck(df):
    df = np.sign(df)
    for row in df.index:
        for col in df.columns[:-3]:
            signCheck = abs(df.loc[row, col] + df.loc[row, col + 1] + df.loc[row, col + 2] + df.loc[row, col + 3])
            if signCheck > 3:
                return 0
    return 1


# Calculate the total distance travelled by each team in the given schedule
def calculateDistance(df_schedule):
    # Represent home games with the team number, and away games with the team number for the opponent
    df = -df_schedule.copy()
    df.columns = df.columns + 1
    for row in df.index:
        df.loc[row][df.loc[row] < 0] = row

    # Add columns to the end and beginning of the schedule representing each team starting and finishing at home
    df.insert(0, 0, list(df.index))
    df.insert(rounds + 1, rounds + 1, list(df.index))

    # Calculate the distance travelled by each team and sum together
    distance = 0
    for row in df.index:
        for col in df.columns[:-1]:
            locOne = df.loc[row, col]
            locTwo = df.loc[row, col + 1]
            distance += df_distMatrix.loc[locOne, locTwo]

    return distance


# Randomly generate a schedule solution
def generateSchedule(_ = []):
    # Prepare variables for usage in the generation loop
    allOptions = [i for i in range(-teams, teams + 1) if i != 0]
    df_template = pd.DataFrame(0, index = range(1, teams + 1), columns = range(games))
    success, columnFailures, homeAwayFailures, internalFailures = 0, 0, 0, 0

    # Attempt to generate a schedule until a valid option is found
    while success == 0:
        df = df_template.copy()

        # Iterate through each column and row
        col = 0
        while col < games:
            for row in df.index:
                proceed = 1
                if df.loc[row, col] == 0:
                    # Check which va
                    valuesInRow = [v for v in list(abs(df.loc[row, :])) if v == v and v != 0]
                    valuesInCol = [v for v in list(abs(df.loc[:, col])) if v == v and v != 0]
                    options = [opt for opt in allOptions if
                               abs(opt) not in valuesInRow and
                               abs(opt) not in valuesInCol and
                               abs(opt) > row]

                    # If there is valid options, place them in the schedule
                    if len(options) > 0:
                        selection = options[randrange(0, len(options))]
                        df.loc[row, col] = selection
                        df.loc[abs(selection), col] = -np.sign(selection) * row

                    # Else if there are no valid options, increment the error counters, reset the column, and try again
                    else:
                        columnFailures += 1
                        internalFailures += 1
                        df.loc[:, col] = 0
                        proceed = 0
                        break

            # If more than ten attempts have been made on a column, reset it and return to the previous column
            if internalFailures > 10:
                col -=1
                df.loc[:, col] = 0
                proceed = 0
                internalFailures = 0

            # If no exceptions were found earlier, proceed to the next column
            if proceed == 1:
                internalFailures = 0
                col += 1

        # Transform the schedule from round robin to double round robin
        df = pd.concat([df, -df], axis = 1, join = 'inner')
        df.columns = range(games * 2)

        # Check that there are not more than three consecutive home/away games
        success = homeAwayCheck(df)
        if success == 0:
            homeAwayFailures += 1

    return df


# Convert the DataFrame representing the schedule into a version readable by humans
def labelledSchedule(df):
    df = df.copy()
    df.index = teamList

    teamDict = {}
    for idx, i in enumerate(teamList):
        teamNo = idx + 1
        teamDict[teamNo] = i
        teamDict[-teamNo] = '@{}'.format(i)

    return df.replace(teamDict).transpose()


# Save schedule (df) to a text file
def saveSchedule(df):
    output = 'Distance:\n{}\n\nMatrix:\n{}\n\nSchedule:\n{}'.format(
        calculateDistance(df),
        df.to_string(index = False, header = False),
        labelledSchedule(df).to_markdown(index = False)
        )

    fileName = 'NL Schedules\\{} teams.txt'.format(teams)
    with open(fileName, 'w') as f:
        f.write(output)


# Load the best saved distance and schedule matrix from the appropriate text file
def loadSavedSchedule():
    fileName = 'NL Schedules\\{} teams.txt'.format(teams)
    try:
        with open(fileName, 'r') as f:
            data = f.read()

        # Get the distance and matrix from the text data
        distance = int(re.findall('Distance:\\n(\d+)\\n', data)[0])
        strMatrix = re.findall('Matrix:\\n(.*?)\\n\\nSchedule', data, flags = re.S)[0]
        df_matrix = pd.DataFrame([x.split() for x in strMatrix.split('\n')], index = range(1, teams + 1))
        df_matrix = df_matrix.astype(int)

    except FileNotFoundError:
        # If the file does not exist, one will be created with a randomly generated schedule
        df_matrix = generateSchedule()
        distance = calculateDistance(df_matrix)
        saveSchedule(df_matrix)

    return distance, df_matrix