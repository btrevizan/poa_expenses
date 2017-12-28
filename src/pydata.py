from .inverted import Inverted
from .pybin import StructFile
from .btree import BTree
from .helper import to_str


class Registry():
    """Represent a registry in database."""

    def __init__(self, table, fmt, pk):
        self.__pk = pk

    @classmethod
    def get_strct(cls):
        return StructFile("database/" + cls.get_table() + '.data', cls.get_fmt())

    @classmethod
    def get_btree(cls):
        return BTree("database/" + cls.get_table() + '.btree')

    def save(self):
        """If object exists, update informations. Insert it, otherwise."""
        if eval('self.{} is None'.format(self.__pk)):
            return self.insert()
        else:
            return self.update()

    def insert(self):
        """Create object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.get_attr(self)

        # Get new id (incremental)
        last = self.last()
        last_pk = 0 if last is None else eval('last.' + self.__pk)
        exec('self.{} = last_pk + 1'.format(self.__pk, self.__pk))
        attrs[self.__pk] = eval('self.{}'.format(self.__pk))

        # Create a tuple of all properties
        data = tuple(attrs.values())

        # Save in file
        strct = self.get_strct()
        strct.append(data)

        # Insert id and file position in BTree
        btree = self.get_btree()
        btree.insert(attrs[self.__pk], strct.length - 1)

        # Return id, if the operation was well successed
        return attrs[self.__pk]

    def update(self, i=None):
        """Update object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.get_attr(self)

        # Create a tuple of all properties
        data = tuple(attrs.values())

        # Get file position
        if i is None:
            btree = self.get_btree()
            i = btree.search(eval('self.' + self.__pk))

        # If registry does not exists...
        if i is None:
            return False

        # Save new data on-disk
        strct = self.get_strct()
        strct.write(i, data)

        return True

    def delete(self):
        """Remove a registry on-disk."""
        # Get last registry in file
        last = self.last()

        # Find this registry position
        this_pk = eval('self.{}'.format(self.__pk))
        last_pk = eval('last.{}'.format(last.get_pk()))

        btree = self.get_btree()
        strct = self.get_strct()

        i = btree.search(this_pk)

        # Overwrite current registry with last
        last.update(i)

        # Remove last from file
        strct.truncate(1)

        # Update BTree
        btree.delete(this_pk)
        btree.delete(last_pk)

        btree.insert(last_pk, i)

    @classmethod
    def select(cls, pks):
        """Select one or more registries according with parameters.

        Keyword arguments:
            pks -- list of primary keys to get
        """
        # Empty list for objects
        objs = list()

        # For each pk...
        for pk in pks:
            obj = cls.get(pk)      # get obj from pk
            objs.append(obj)        # save object

        return objs

    @classmethod
    def get(cls, pk):
        """Get a registry from pk.

        Keyword argument:
            pk -- primary key
        """
        strct = cls.get_strct()
        btree = cls.get_btree()

        i = btree.search(pk)  # get registry position in file

        if i is None:
            return None

        data = strct.get(i)   # get data in file
        obj = cls.object(data)      # create an object from data

        return obj

    @classmethod
    def all(cls):
        """Get all records."""
        strct = cls.get_strct()
        records = strct.get(0, strct.length)
        return [cls.object(r) for r in records]

    @classmethod
    def object(cls, values):
        """Receive a tuple with data and return an object.

        Keyword arguments:
            values -- tuple with data
        """
        attrs = cls.get_attr(cls)  # get attribute
        keys = list(attrs.keys())  # get attributes' name
        keys = keys[:len(values)]

        n = len(keys)              # number of attributes

        # Create a dict with key, value
        data = dict()

        for i in range(n):
            data[keys[i]] = values[i]

            if type(values[i]) is bytes:
                data[keys[i]] = values[i].decode('utf-8')
                data[keys[i]] = data[keys[i]].replace('\x00', '')

        # Return an object
        return cls(**data)

    @classmethod
    def last(cls):
        """Get the lastest inserted element."""
        data = cls.get_strct().last()
        return None if data is None else cls.object(data)

    @staticmethod
    def get_attr(obj):
        # Get objects attributes as {attribute_name: value}
        attrs = obj.__dict__

        # Unzip attrs dict
        key, value = zip(*attrs.items())

        # Create a tuple of all properties
        data = dict()

        for k in key:
            if '__' not in k and not callable(attrs[k]):
                data[k] = attrs[k]

                if type(attrs[k]) is str:
                    data[k] = bytes(data[k], encoding='utf-8')

        return data

    @classmethod
    def get_inverted(cls, suffix=''):
        return Inverted('database/' + cls.get_table() + suffix)

    def __eq__(self, other):
        return eval('self.{} == other.{}'.format(self.__pk, self.__pk))

    def __str__(self):
        attrs = self.get_attr(self)

        string = ''
        for key in attrs:
            string += '{}: {}\n'.format(key.upper(), eval('self.' + key))

        return string[:-1]

    def __repr__(self):
        attrs = self.get_attr(self)

        string = ''
        for key in attrs:
            string += str(eval('self.' + key)) + ';'

        return string[:-1]

class Department(Registry):
    """Represent a Department registry.

    Properties:
        id -- code
        name -- department's name
    """
    id = None
    name = ''

    __table = 'department'
    __fmt = 'I100s'
    __pk = 'id'

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- department's name (default '')
        """
        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)

    @classmethod
    def get_table(cls):
        return cls.__table

    @classmethod
    def get_fmt(cls):
        return cls.__fmt

    @classmethod
    def get_pk(cls):
        return cls.__pk

    def insert(self):
        """Insert as super and add name in inverted file."""
        # Save as super
        id = super().insert()

        # Insert in inverted file
        inverted = self.get_inverted()     # open file
        inverted.insert(self.name, id)     # insert

        return id

    def update(self, i=None):
        """Update a record."""
        record = self.get(self.id)

        super().update(i)

        inverted = self.get_inverted()              # open file
        inverted.update(record.name, self.name)     # update

    @classmethod
    def select(cls, name):
        """Select by name.

        Keyword argument:
            name -- department name (str)
        """
        # Clear string
        name = to_str(name)

        # Get ids
        inv = cls.get_inverted()
        ids = inv.get(name)

        # Get objects from ids
        return super().select(ids)

    def delete(self):
        """Remove a registry on-disk."""
        super().delete()

        inverted = self.get_inverted()          # open file
        inverted.delete(self.name, self.id)     # delete

        # Delete subdepartments
        sub_inv = Subdepartment.get_inverted()
        sub_ids = sub_inv.get(self.id)

        for sid in sub_ids:
            subdep = Subdepartment.get(sid)
            subdep.delete()

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

    __table = 'subdepartment'
    __fmt = 'I100sI'
    __pk = 'id'

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- department's name (default '')
            department_id -- department code (default None)
        """
        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)
        self.department_id = kwargs.get('department_id', self.department_id)

    @classmethod
    def get_table(cls):
        return cls.__table

    @classmethod
    def get_fmt(cls):
        return cls.__fmt

    @classmethod
    def get_pk(cls):
        return cls.__pk

    def insert(self):
        """Insert as super and add name in inverted file."""
        # Save as super
        id = super().insert()

        # Insert in inverted file
        inverted = self.get_inverted()              # open file
        inverted.insert(self.department_id, id)     # insert

        inverted = self.get_inverted('_name')       # open file
        inverted.insert(self.name, id)              # insert

        return id

    def update(self, i=None):
        """Update a record."""
        record = self.get(self.id)

        super().update(i)

        inverted = self.get_inverted()                                # open file
        inverted.update(record.department_id, self.department_id)     # update

        inverted = self.get_inverted('_name')                         # open file
        inverted.update(record.name, self.name)                       # update

    @classmethod
    def select(cls, **kwargs):
        """Select by name.

        Keyword argument:
            dep_id -- department id (default None)
            name -- subdepartment's name (default '')
        """
        dep_id = kwargs.get('dep_id', None)
        name = kwargs.get('name', '')

        if dep_id:
            # Get ids
            inv = cls.get_inverted()
            ids = inv.get(dep_id)

            # Get objects from ids
            return super().select(ids)

        if len(name):
            # Get ids
            inv = cls.get_inverted('_name')
            ids = inv.get(name)

            # Get objects from ids
            return super().select(ids)

    def delete(self):
        """Remove a registry on-disk."""
        super().delete()

        inverted = self.get_inverted()                   # open file
        inverted.delete(self.department_id, self.id)     # delete

        inverted = self.get_inverted('_name')    # open file
        inverted.delete(self.name, self.id)      # delete

        # Delete employees
        emp_inv = Employee.get_inverted()
        emp_ids = emp_inv.get(self.id)

        for eid in emp_ids:
            employee = Employee.get(eid)
            employee.delete()


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

    __table = 'employee'
    __fmt = 'I70sI'
    __pk = 'id'

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            name -- employee's name (default '')
            subdepartment_id -- subdepartment code (default None)
        """
        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)
        self.subdepartment_id = kwargs.get('subdepartment_id', self.subdepartment_id)

    @classmethod
    def get_table(cls):
        return cls.__table

    @classmethod
    def get_fmt(cls):
        return cls.__fmt

    @classmethod
    def get_pk(cls):
        return cls.__pk

    def insert(self):
        """Insert as super and add name in inverted file."""
        # Save as super
        id = super().insert()

        # Insert in inverted file
        inverted = self.get_inverted()                # open file
        inverted.insert(self.subdepartment_id, id)    # insert

        inverted = self.get_inverted('_name')         # open file
        inverted.insert(self.name, id)                # insert

        return id

    def update(self, i=None):
        """Update a record."""
        record = self.get(self.id)

        super().update(i)

        inverted = self.get_inverted()                                   # open file
        inverted.update(record.subdepartment_id, self.subdepartment_id)  # update

        inverted = self.get_inverted('_name')                            # open file
        inverted.update(record.name, self.name)                          # update

    @classmethod
    def select(cls, **kwargs):
        """Select by name.

        Keyword argument:
            dep_id -- department id (default None)
            subdep_id -- subdepartment id (default None)
            name -- employee's name (default '')

        When dep_id is set, subdep_id is ignored. The other way around also applies.
        """
        # Get params
        dep_id = kwargs.get('dep_id', None)         # department id
        subdep_id = kwargs.get('subdep_id', None)   # subdepartment id
        name = kwargs.get('name', '')               # employee's name

        # If dep_id is set
        if dep_id:
            subdep_inv = Subdepartment.get_inverted()
            subdep_ids = subdep_inv.get(dep_id)

            objs = list()
            for sid in subdep_ids:
                objs += cls.select(subdep_id=sid, name=name)

            return objs

        # If subdep_id is set
        if subdep_id:
            # Get ids
            inv = cls.get_inverted()
            ids = inv.get(subdep_id)

            # Get objects from ids
            return super().select(ids)

        # If name is set
        if len(name):
            # Get ids
            inv = cls.get_inverted('_name')
            ids = inv.get(name)

            # Get objects from ids
            return super().select(ids)

    def delete(self):
        """Remove a registry on-disk."""
        super().delete()

        inverted = self.get_inverted()                      # open file
        inverted.delete(self.subdepartment_id, self.id)     # delete

        inverted = self.get_inverted('_name')    # open file
        inverted.delete(self.name, self.id)      # delete

        # Delete transactions
        trans_inv = Transaction.get_inverted()
        trans_ids = trans_inv.get(self.id)

        for tid in trans_ids:
            transaction = Transaction.get(tid)
            transaction.delete()


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

    __table = 'transaction'
    __fmt = '2I2000sfL'
    __pk = 'id'

    def __init__(self, **kwargs):
        """Set Department data.

        Keyword arguments:
            id -- code (default None)
            employee_id -- employee code (default None)
            description -- transaction's description (default '')
            value -- transaction's value (default 0)
            date -- transaction's date as timestamp (default 0)
        """
        super().__init__(self.__table, self.__fmt, self.__pk)

        self.id = kwargs.get('id', self.id)
        self.employee_id = kwargs.get('employee_id', self.employee_id)
        self.description = kwargs.get('description', self.description)
        self.value = kwargs.get('value', self.value)
        self.date = kwargs.get('date', self.date)

    @classmethod
    def get_table(cls):
        return cls.__table

    @classmethod
    def get_fmt(cls):
        return cls.__fmt

    @classmethod
    def get_pk(cls):
        return cls.__pk

    def insert(self):
        """Insert as super and add name in inverted file."""
        # Save as super
        id = super().insert()

        # Insert in inverted file
        inverted = self.get_inverted()         # open file
        inverted.insert(self.employee_id, id)  # insert

        return id

    def update(self, i=None):
        """Update a record."""
        record = self.get(self.id)

        super().update(i)

        inverted = self.get_inverted()                         # open file
        inverted.update(record.employee_id, self.employee_id)  # update

    @classmethod
    def select(cls, **kwargs):
        """Select by name.

        Keyword argument:
            employee_id -- employee's id (default None)
            description -- transaction's description (default '')
        """
        employee_id = kwargs.get('employee_id', None)
        description = kwargs.get('description', '')

        if employee_id:
            # Get ids
            inv = cls.get_inverted()
            ids = inv.get(employee_id)

            # Get objects from ids
            objs = super().select(ids)
            objs = filter(lambda x: description in x.description, objs)

            return list(objs)

    def delete(self):
        """Remove a registry on-disk."""
        super().delete()

        inverted = self.get_inverted()                  # open file
        inverted.delete(self.employee_id, self.id)      # delete

