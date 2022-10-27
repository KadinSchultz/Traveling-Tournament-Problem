# Custom packages
from config import popSize, genCount, nThreads
import schedules
import mutations

# Third-party packages
import multiprocessing as mp
from datetime import datetime
from sys import stdout


# Return the current time formatted in HH:MM:SS
def currentTime():
    return datetime.now().strftime('%H:%M:%S')


# Return a string representing the hh:mm:ss difference between the time passed and the current time
def timeSince(timeStart):
    # Current time
    timeEnd = datetime.now()

    # Difference between the time passed to the function, and the current time
    timeDiff = timeEnd - timeStart

    # Convert the time difference into components
    seconds = timeDiff.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Return the formatted string
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)


# Return an estimate of how much longer the program will take to execute
def timeRemaining(g, timeStart):
    # Current time
    timeEnd = datetime.now()

    # Estimate time required for remaining generations
    timeDiff = timeEnd - timeStart
    timeEst = timeDiff * (genCount - g - 1)

    # Convert the time difference into components
    seconds = timeEst.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Return the formatted string
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)


if __name__ == '__main__':
    print('{} --- Program execution begun'.format(currentTime()))

    # Initialise the population
    timeStart = datetime.now()
    with mp.Pool(processes = nThreads) as pool:
        pop = pool.map(schedules.generateSchedule, range(popSize))

    # Load the previous best schedule, and append it to the population
    bestDistance, df = schedules.loadSavedSchedule()
    pop.append(df)
    print('{} --- Pop initialised in: {}, best distance: {}'.format(currentTime(), timeSince(timeStart), bestDistance))


    # Process each generation
    for g in range(genCount):
        timeStart_gen = datetime.now()

        # Mutate all parents in the population
        with mp.Pool(processes = nThreads) as pool:
            children = pool.map(mutations.mutate, pop)


        # Remove children that already exist in the population, and append the unique/new ones
        idx = [any([p.equals(c) for p in pop]) for c in children]
        children = [d for (d, remove) in zip(children, idx) if not remove]
        pop.extend(children)


        # Calculate the distances for the population
        with mp.Pool(processes = nThreads) as pool:
            dists = pool.map(schedules.calculateDistance, pop)


        # Sort the population by distance, and remove the worse half
        pop = [x for _, x in sorted(zip(dists, pop), key = lambda x: x[0])]
        pop = pop[:popSize]


        # If the schedule with the lowest distance beats the current high score, replace it
        if min(dists) < bestDistance:
            bestDistance = min(dists)
            schedules.saveSchedule(pop[0])


        # Print the most recent statistics to the command line
        txt = '\r{} --- Gen {}/{} complete in: {}, best distance: {}, est. remaining time: {}'.format(currentTime(), g + 1, genCount, timeSince(timeStart_gen), bestDistance, timeRemaining(g, timeStart_gen))
        stdout.write(txt)
        stdout.flush()


    # Print the final statistics to the command line
    txt = '\n{} --- Program complete in: {}, best distance: {}'.format(currentTime(), timeSince(timeStart), bestDistance)
    print(txt)
