from .pybin import StructFile
from .btree import BTree


class Registry():
    """Represent a registry in database."""

    def __init__(self, table, fmt, pk):
        self.__pk = pk
        self.__strct = StructFile("database/" + table + '.data', fmt)
        self.__btree = BTree("database/" + table + '.btree', fmt)

    def save(self):
        """If object exists, update informations. Insert it, otherwise."""
        if eval('self.{} is None'.format(self.__pk)):
            self.insert()
        else:
            self.update()

    def insert(self):
        """Create object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.__get_attr()

        # Get new id (incremental)
        last = self.last()
        exec('self.{} = last.{} + 1'.format(self.__pk, self.__pk))
        attrs[self.__pk] = eval('self.{}'.format(self.__pk))

        # Create a tuple of all properties
        data = tuple(attrs.values())

        # Save in file
        self.__strct.append(data)

        # Insert id and file position in BTree
        self.__btree.insert(attrs[self.__pk], self.__strct.length - 1)

        # Return id, if the operation was well successed
        return attrs[self.__pk]

    def update(self):
        """Update object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.__get_attr()

        # Create a tuple of all properties
        data = tuple(attrs.values())

        # Get file position
        i = self.__btree.search(eval('self.' + self.__pk))

        # If registry does not exists...
        if i is None:
            return False

        # Save new data on-disk
        self.__strct.write(i, data)

        return True

    def delete(self):
        pass

    def select(self, pks):
        """Select one or more registries according with parameters.

        Keyword arguments:
            pks -- list of primary keys to get
        """
        # Empty list for objects
        objs = list()

        # For each pk...
        for pk in pks:
            i = self.__btree.search(pk)  # get registry position in file
            data = self.__strct.get(i)   # get data in file
            obj = self.object(data)      # create an object from data
            objs.append(obj)             # save object

        return objs

    @classmethod
    def object(cls, data):
        """Receive a tuple with data and return an object.

        Keyword arguments:
            data -- tuple with data
        """
        attrs = self.__get_attr()  # get attribute
        keys = list(attrs.keys())  # get attributes' name

        n = len(keys)              # number of attributes

        # Create a dict with key, value
        data = {kwargs[keys[i]]: data[i] for i in range(n)}

        # Return an object
        return cls(**data)

    @classmethod
    def last(cls):
        """Get the lastest inserted element."""
        data = cls.__strct.last()
        return cls.object(data)

    def __get_attr(self):
        # Get objects attributes as {attribute_name: value}
        attrs = self.__dict__

        # Unzip attrs dict
        key, value = zip(*attrs.items())

        # Create a tuple of all properties
        data = {k: attrs[k] for k in key if '__' not in k}

        return data


class Department(Registry):
    """Represent a Department registry.

    Properties:
        id -- code
        name -- department's name
    """
    id = None
    name = ''

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- department's name (default '')
        """
        self.__table = 'department'
        self.__fmt = 'I50s'
        self.__pk = 'id'

        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)


class Subdepartment(Registry):
    """Represent a Subdepartment registry.

    Properties:
        id -- code
        name -- department's name
        department_id -- department code
    """
    id = None
    name = ''
    department_id = None

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- department's name (default '')
            department_id -- department code (default None)
        """
        self.__table = 'subdepartment'
        self.__fmt = 'I50sI'
        self.__pk = 'id'

        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)
        self.department_id = kwargs.get('department_id', self.department_id)


class Employee(Registry):
    """Represent a Employee registry.

    Properties:
        id -- code
        name -- employee's name
        subdepartment_id -- subdepartment code
    """
    id = None
    name = ''
    subdepartment_id = None

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- employee's name (default '')
            subdepartment_id -- subdepartment code (default None)
        """
        self.__table = 'employee'
        self.__fmt = 'I100sI'
        self.__pk = 'id'

        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)
        self.subdepartment_id = kwargs.get('subdepartment_id', self.subdepartment_id)


class Transaction(Registry):
    """Represent a Transaction registry.

    Properties:
        id -- code
        employee_id -- employee code
        description -- transaction's description
        value -- transaction's value
        date -- transaction's date as timestamp
    """
    id = None
    employee_id = None
    description = ''
    value = 0
    date = 0

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            employee_id -- employee code (default None)
            description -- transaction's description (default '')
            value -- transaction's value (default 0)
            date -- transaction's date as timestamp (default 0)
        """
        self.__table = 'transaction'
        self.__fmt = '2I900sfL'
        self.__pk = 'id'

        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.employee_id = kwargs.get('employee_id', self.employee_id)
        self.description = kwargs.get('description', self.description)
        self.value = kwargs.get('value', self.value)
        self.date = kwargs.get('date', self.date)

