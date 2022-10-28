# Traveling Tournament Problem
This repository contains the files and code I've written to generate near-optimal solutions to Michael Trick's Traveling Tournament Problem (TTP), using an evolutionary algorithm.

> The Travelling Tournament Problem is a sports timetabling problem requiring production of a minimum distance double round-robin tournament for a group of n teams. Even small instances of this problem seem to be very difficult to solve. In this paper, we present the first provably optimal solution for an instance of eight teams. The solution methodology is a parallel implementation of a branch-and-price algorithm that uses integer programming to solve the master problem and constraint programming to solve the pricing problem. Additionally, constraint programming is used as a primal heuristic.

(Easton, Nemhauser, & Trick, 2001)

Whilst typically an exercise in constraint programming and optimisation, this code will use randomly generated schedules and mutations in an evolutionary algorithm to create mirrored round-robin instances for the 'National League' (NL) datasets.

## Schedule Matrix
The program stores schedules as a DataFrame. Each team is assigned an integer, each row within the DataFrame represents a team's home/away games, and each column is a round within the schedule. Negative values represent away games.

For instance, the NL4 setup uses the following teams: ATL, NYM, PHI, MON. The following is a potential schedule:
| Round | ATL   | NYM   | PHI   | MON   |
|:------|:------|:------|:------|:------|
| 1     | PHI   | MON   | @ATL  | @NYM  |
| 2     | NYM   | @ATL  | MON   | @PHI  |
| 3     | MON   | @PHI  | NYM   | @ATL  |
| 4     | @PHI  | @MON  | ATL   | NYM   |
| 5     | @NYM  | ATL   | @MON  | PHI   |
| 6     | @MON  | PHI   | @NYM  | ATL   |

In rounds 1-3, ATL plays PHI, NYM, then MON at ATL's home. In rounds 4-6, ATL plays PHI, NYM, and MON at their respective homes. Replacing the team names with integers, and representing away games with negative values results in the below representation.
### Team Values
| Team | INT |
|:-----|:----|
| ATL  | 1   |
| NYM  | 2   |
| PHI  | 3   |
| MON  | 4   |

### Schedule with Values
| Round | ATL   | NYM   | PHI   | MON   |
|:------|:------|:------|:------|:------|
| 1     | 3     | 4     | -1    | -2    |
| 2     | 2     | -1    | 4     | -3    |
| 3     | 4     | -3    | 2     | -1    |
| 4     | -3    | -4    | 1     | 2     |
| 5     | -2    | 1     | -4    | 3     |
| 6     | -4    | 3     | -2    | 1     |

### Schedule DataFrame (transpose of above)
| Team # | Game 1 | Game 2 | Game 3 | Game 4 | Game 5 | Game 6 |
|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| 1      | 3      | 2      | 4      | -3     | -2     | -4     |
| 2      | 4      | -1     | -3     | -4     |  1     | 3      |
| 3      | -1     | 4      | 2      | 1      | -4     | -2     |
| 4      | -2     | -3     |-1      | 2      | 3      | 1      |

## Files
### main.py
Execute this script to run the program. This file creates the initial population using functions from schedules.py, and executes each generation with the evolutionary loop shown below. The script also saves the best schedule (least distance travelled) whenever the 'high score' is beaten.

Evolutionary algorithm:
1. Generate the initial population.
2. Import the current 'best' schedule, and append to the population.
3. Mutate each existing schedule (create children).
4. Remove any children that already exist in the population.
5. Combine the parents and children.
6. Calculate the fitness (total distance travelled) for each member of the population.
7. Cull the worse half of the population.
8. If the 'best' schedule is beaten, save the new 'best' to the specified text file.
9. Return to step 3, and repeat as required.

### config.py
This file contains the basic variables required by ```main.py```, ```schedules.py```, and ```mutations.py```, including the number of teams, population size, number of generations, and how many processes to use when multiprocessing, for example.

### schedules.py
This module contains the functions required to generate a schedule, ensure validity, and calculate the total distance travelled. There is additional funcionality for neatly formatting the schedule for readability, and saving/loading schedules from a text file.

### mutations.py
This module contains the functions required to mutate schedules within the evolutionary loop. The function ```mutate()``` selects which of the mutations is applied, or potentially replaces the input schedule with one that's freshly generated. To illustrate the mutations, we will start with the below schedule.
| G1 | G2 | G3 | G4 | G5 | G6 |
|:---|:---|:---|:---|:---|:---|
| 3  | 2  | 4  | -3 | -2 | -4 |
| 4  | -1 | -3 | -4 | 1  | 3  |
| -1 | 4  | 2  | 1  | -4 | -2 |
| -2 | -3 | -1 | 2  | 3  | 1  |

```swapGameSlots()``` switches two game rounds within a schedule, per side of the mirrored round-robin. In the below example, games one and three (G1, G3) are swapped, and thus so are their counterparts on the mirrored round-robin (G4, G5).
| G1 | G2 | G3 | G4 | G5 | G6 |
|:---|:---|:---|:---|:---|:---|
| 4  | 2  | 3  | -4 | -2 | -3 |
| -3 | -1 | 4  | 3  | 1  | -4 |
| 2  | 4  | -1 | 2  | -4 | 1  |
| -1 | -3 | -2 | 1  | 3  | 2  |

```invertSlot()``` inverts the home/away assignments within a single round of the schedule, per side of the mirrored round-robin. In the below example, game one is inverted (G1 and G4).
| G1 | G2 | G3 | G4 | G5 | G6 |
|:---|:---|:---|:---|:---|:---|
| -3 | 2  | 4  | 3  | -2 | -4 |
| -4 | -1 | -3 | 4  | 1  | 3  |
| 1  | 4  | 2  | -1 | -4 | -2 |
| 2  | -3 | -1 | -2 | 3  | 1  |


```invertSchedule()``` reverses the home/away assignments for all games in a schedule. For example:
Becomes the below when mutated:
| G1 | G2 | G3 | G4 | G5 | G6 |
|:---|:---|:---|:---|:---|:---|
| -3 | -2 | -4 | 3  | 2  | 4  |
| -4 | 1  | 3  | 4  | -1 | -3 |
| 1  | -4 | -2 | -1 | 4  | 2  |
| 2  | 3  | 1  | -2 | -3 | -1 |

## Folders
### Distance Matrices
This folder contains the distance matrices for each potential number of teams in the NL. This matrix illustrates the distance between each team's respective stadium.

### NL Schedules
This folder contains the text files output with the best scoring schedules for each potential number of teams.

## References

Easton, K., Nemhauser, G., & Trick, M. (2001). Solving the Traveling Tournament Problem: A Combined Integer Programming and Constraint Programming Approach. Lecture Notes in Computer Science. Tepper School of Business.
