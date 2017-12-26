import pickle
from .pybin import StructFile
from .pysort import timsort


class Inverted():
    """Inverted file for string indexing."""

    def __init__(self, filename):
        """Set properties.

        Keyword arguments:
            filepath -- path to inverted file
        """
        try:
            # If file exists, open and load
            dict_file = open(filename + '.dict', 'rb')  # open file
            self.__dict = pickle.load(dict_file)        # load content
            dict_file.close()                           # close file
        except FileNotFoundError:
            # Create new dict, otherwise
            self.__dict = dict()

            # And save in file
            dict_file = open(filename + '.dict', 'wb')  # open file
            pickle.dump(self.__dict, dict_file)         # save content
            dict_file.close()                           # close file

        self.__n = 121
        self.__filename = filename
        self.__file = StructFile(filename + '.inv', str(self.__n) + 'i')

    @property
    def n_keys(self):
        return self.__n - 1

    def insert(self, key, value):
        """Insert a value for a key.

        Keyword arguments:
            key -- key in dict
            value -- key's value
        """
        i = self.__dict.setdefault(key, self.__file.length)

        # Check if list does not exist
        if i == self.__file.length:
            values = [value]
            values += [-1] * self.n_keys

            self.__file.append(values)
        else:
            vals, pos = self.__get(i)

            # Get elements from last list
            j = len(vals) // self.n_keys
            j = j * self.n_keys

            values = vals[j:]

            # If there is no element...
            if len(values) == 0:
                # It means that values are full
                i = self.__file.length              # get file length
                values = vals[-self.n_keys:]        # get last list
                values.append(i)                    # save file index as last element
                self.__save(pos[-1], values)        # save last list
                values = [value]                    # create a new list to save value
                self.__save(i, values)              # save value on last index
            # There is element and it's not full
            else:
                values.append(value)                # append value
                values = timsort(values)            # sort values
                self.__save(pos[-1], values)        # save on list position

    def __get(self, i):
        """Get values from ith element in file.

        Return a tuple as (<values>, <file positions>).

        Keyword argument:
            i -- ith element
        """
        values = self.__file.get(i)                         # get values from file
        values = list(filter(lambda x: x > -1, values))     # clear values
        all_values = list()                                 # empty list to save all values
        positions = [i]                                     # list of positions

        while len(values) == self.__n:
            all_values += values[:-1]                           # save values
            positions.append(values[-1])                        # save position

            i = positions[-1]                                   # get last position
            values = self.__file.get(i)                         # get values from file
            values = list(filter(lambda x: x > -1, values))     # clear values

        all_values += values                                    # save last values

        # Return values and positions
        return all_values, positions

    def get(self, key):
        """Get list of values from key.

        Keyword argument:
            key -- dict's key
        """
        i = self.__dict[key]            # get file position
        values, _ = self.__get(i)       # get values
        return values                   # return values

    def __save(self, i, values):
        """Prepare data and save on-disk.

        Keyword arguments:
            i -- position in file
            values -- list of values to be saved
        """
        values += [-1] * (self.__n - len(values))   # fill with -1
        self.__file.write(i, values)                # save on-disk

    def __del__(self):
        file = open(self.__filename + '.dict', 'wb')  # open file
        pickle.dump(self.__dict, file)                # save content
        file.close()                                  # close file


