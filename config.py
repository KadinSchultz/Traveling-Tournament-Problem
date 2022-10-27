from pandas import DataFrame


# Load the distance matrix and team names from a text file
def loadTeamFiles(teams):
    # Distance matrix
    fileName = 'Distance Matrices\\NL{}.txt'.format(str(teams))
    with open(fileName) as file:
        distMatrix = []
        for line in file:
            line = line.split()
            if line:
                line = [int(i) for i in line]
                distMatrix.append(line)

    df = DataFrame(distMatrix)
    df.columns = range(1, teams + 1)
    df.index = range(1, teams + 1)

    # List of teams
    fileName = 'Distance Matrices\\NL Teams.txt'
    with open(fileName) as file:
        teamList = file.read().split()

    teamList = teamList[:teams]

    return df, teamList


teams = 8
games = teams - 1
rounds = 2 * games
df_distMatrix, teamList = loadTeamFiles(teams)

popSize = 500
genCount = 100
nThreads = 8