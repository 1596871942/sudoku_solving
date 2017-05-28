

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [x+y for x in A for y in B];

cols = '123456789';
rows = 'ABCDEFGHI';
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [[rows[i] + cols[i] for i in range(9)], [rows[::-1][i] + cols[i] for i in range(9)]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    for key in values:
        for cohort in units[key]:
            removeMe = [];
            for subkey in cohort:
                for checkkey in cohort:
                    if len(values[subkey]) == 2 and len(values[checkkey]) == 2 and subkey != checkkey and values[subkey] == values[checkkey]:
                        removeMe = list(values[subkey]);
                        notSubkey = subkey;
                        notCheckkey = checkkey;
            if len(removeMe) > 0:
                for x in cohort:
                    newVal = [];
                    if x != notSubkey and x != notCheckkey:
                        checkVal = list(values[x])
                        for y in checkVal:
                            if y not in removeMe:
                                newVal.append(y);
                        useVal = ''.join(newVal);
                        values[x] = useVal;
    return values;

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers



def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    keys = cross(rows,cols);
    values = list(grid);
    answer = {};
    i = 0;
    for key in keys:
        if values[i] != '.':
            answer[key] = values[i];
        else:
            answer[key] = '123456789';
        i+=1;
    return answer;



def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key in values:
        if len(values[key]) == 1:
            for subkey in peers[key]:

                values[subkey] = values[subkey].replace(values[key],"");



    return values;


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """

    for key in values:
        for subkey in units[key]:

            valObj = {};
            killArray = [];
            choiceArray = [];
            for finalkey in subkey:
                valObj[finalkey] = values[finalkey];
                choiceArray.append(list(values[finalkey]));
                if len(values[finalkey]) == 1:
                    killArray.append(values[finalkey]);
            flatArray = [];
            for x in choiceArray:
                for y in x:
                    flatArray.append(y);

            finalChoice = [x for x in flatArray if x not in killArray];
            singlets = [x for x in finalChoice if finalChoice.count(x) == 1]

            for z in singlets:
                for ez in valObj:
                    # for kill in killArray:
                    #     if len(valObj[ez]) > 1:
                    #         valObj[ez] = valObj[ez].replace(kill, "");
                    if valObj[ez].find(z) != -1:
                        valObj[ez] = z;
                    values[ez] = valObj[ez];

    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        for key in values:
            if len(values[key]) == 1:
                for subkey in peers[key]:
                    values[subkey] = values[subkey].replace(values[key],"");
        # TODO: Implement only choice strategy here
        for key in values:
            for subkey in units[key]:
                # print("in this unit we have:");
                valObj = {};
                killArray = [];
                choiceArray = [];
                for finalkey in subkey:
                    valObj[finalkey] = values[finalkey];
                    choiceArray.append(list(values[finalkey]));
                    if len(values[finalkey]) == 1:
                        killArray.append(values[finalkey]);
                flatArray = [];
                for x in choiceArray:
                    for y in x:
                        flatArray.append(y);

                finalChoice = [x for x in flatArray if x not in killArray];
                singlets = [x for x in finalChoice if finalChoice.count(x) == 1]

                for z in singlets:
                    for ez in valObj:
                        # for kill in killArray:
                        #     if len(valObj[ez]) > 1:
                        #         valObj[ez] = valObj[ez].replace(kill, "");
                        if valObj[ez].find(z) != -1:
                            valObj[ez] = z;
                        values[ez] = valObj[ez];

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    values = reduce_puzzle(values)
    # Choose one of the unfilled squares with the fewest possibilities
    if values is False:
        return False;
    if all(len(values[x]) == 1 for x in values):
        return values;
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid);
    return search(values);
