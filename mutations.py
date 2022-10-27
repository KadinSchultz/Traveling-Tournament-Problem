from config import games, rounds
from schedules import homeAwayCheck, generateSchedule

from itertools import combinations
from random import choice


# Switch two rounds (slots) within a schedule (per side of the round robin)
def swapGameSlots(df):
    validity = 0
    df_backup = df.copy()
    columnCombinations = list(combinations(list(df.columns[:games]), 2))

    # Whilst the output is invalid, or until there are no more valid combinations
    while validity == 0 and len(columnCombinations) > 0:
        df = df_backup.copy()
        columns = list(df.columns[:games])

        # Select which columns to swap, and remove them from the list of options
        selection = choice(columnCombinations)
        col1, col2 = selection[0], selection[1]
        columnCombinations.remove(selection)

        # Get the new order for the columns
        columns[col1], columns[col2] = columns[col2], columns[col1]
        columns += [c + games for c in columns]

        # Adjust the columns (rounds) within the schedule
        df = df.reindex(columns = columns)
        df.columns = list(range(rounds))

        # Check if the mutated schedule still meets the no-more-than three consecutive home/away games constraint
        validity = homeAwayCheck(df)

    if validity == 0:
        df = df_backup.copy()

    return df, validity


# Invert the home/away allocations within a single round (slot) in a schedule (per side of the round robin)
def invertSlot(df):
    validity = 0
    df_backup = df.copy()
    columns = list(df.columns[:games])

    # Whilst the output is invalid, or until there are no more valid columns
    while validity == 0 and len(columns) > 0:

        df = df_backup.copy()

        # Select whilc column to invert, and remove it from the list of options
        col = choice(columns)
        columns.remove(col)

        # Invert the column in either side of the round robin
        df.loc[:, col] = -df.loc[:, col]
        df.loc[:, col + games] = -df.loc[:, col + games]

        # Check if the mutated schedule still meets the no-more-than three consecutive home/away games constraint
        validity = homeAwayCheck(df)

    if validity == 0:
        df = df_backup.copy()

    return df, validity


# Invert the entire schedule (home -> away, away -> home)
def invertSchedule(df):
    return -df, 1


# Randomly select a mutation, and apply it to the schedule
def mutate(df):
    # List of valid mutation functions, including the option to create a new random schedule
    options = [generateSchedule, swapGameSlots, invertSlot, invertSchedule]

    validity = 0
    while validity != 1:
        # Randomly select a mutation, and remove it from the list of potential options
        mutation = choice(options)
        options.remove(mutation)

        # The function to generate a new schedule does not require self.matrix to be passed, and does not return a validity flag
        if mutation != generateSchedule: df, validity = mutation(df)
        else: df, validity = generateSchedule(), 1

    return df