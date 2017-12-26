"""Sort algorithm adapted from https://github.com/btrevizan/ordernsearch.git."""


def def_key(x):
    """Return the element to compare with.

    Keyword arguments:
        x -- object of any kind
    """
    return x


def timsort(sequence, key=def_key):
    """Tim sort implementation.

    Keyword arguments:
        sequence -- a 1darray to order
        key -- function that retrive a singular element
        (default is the element itself)
    """
    n = len(sequence)       # number of elements
    r = 16                  # length of runs

    # For each run, sort with insertion
    for i in range(0, n, r):
        # Sort with insertion
        sequence[i:i + r] = insertion(sequence[i:i + r], key)

    # For each run, pairwise merge
    while r < n:
        for i in range(0, n - r, r * 2):
            left = i           # left head's index
            right = i + r      # right head's index

            # Divide sequences
            sequence1 = sequence[left:right]
            sequence2 = sequence[right:right + r]

            # Merge sequences
            sequence[left:right + r] = __simplemerge(sequence1, sequence2, key)

        r = r * 2

    return sequence


def insertion(sequence, key=def_key):
    """Insertion sort with sequencial search.

    Keyword arguments:
        sequence -- a 1darray to order
        key -- function that retrive a singular element
        (default is the element itself)
    """
    n = len(sequence)  # number of elements

    # For each element...
    for i in range(1, n):
        value = sequence[i]

        # For each element already sorted...
        j = i - 1       # index of prev element
        while j >= 0:

            # Compare elements
            changed = key(value) < key(sequence[j])
            if not changed:
                break

            # Move the element forward by 1
            sequence[j + 1] = sequence[j]

            # Update j
            j = j - 1

        # Insert element after sequence[j]
        sequence[j + 1] = value

    return sequence


def __simplemerge(sequence1, sequence2, key=def_key):
    """Merge two sequences. The result is a sorted list.

    Keyword arguments:
        sequence1 -- sequence to be merge to the other
        sequence2 -- other
        key -- function that retrive a singular element
        (default is the element itself)
    """

    n1 = len(sequence1)  # sequence's 1 length
    n2 = len(sequence2)  # sequence's 2 length
    l = 0                # left's index
    r = 0                # right's index

    # List with merged elements (sorted too)
    merge = list()

    # For each element on both sequences...
    for i in range(n1 + n2):

        left = sequence1[l]     # left element
        right = sequence2[r]    # right element

        # Compare elements
        if key(left) < key(right):
            merge.append(left)
            l += 1
        else:
            merge.append(right)
            r += 1

        # End of left segment, concat right segment
        if l == len(sequence1):
            for j in range(r, len(sequence2)):
                merge.append(sequence2[j])

            break

        # End of right segment, concat left segment
        if r == len(sequence2):
            for j in range(l, len(sequence1)):
                merge.append(sequence1[j])

            break

        # Update i
        i += 1

    return merge
