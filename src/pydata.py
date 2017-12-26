from .pybin import StructFile


class Registry():
    """Represent a registry in database."""

    def __init__(self, table, fmt):
        self.__strct = StructFile("database/" + table, fmt)

    def save(self):
        """If object exists, update informations. Insert it, otherwise."""
        if self.id is None:
            self.insert()
        else:
            self.update()

    def insert(self):
        """Create object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.__get_attr()

        # Get new id (incremental)
        last = self.last()
        self.id = last.id + 1
        attrs[self.__pk] = attrs[self.__pk]

        # Create a tuple of all properties
        data = tuple(attrs.values())

        # Save in file
        self.__strct.append(data)

        # Return id, if the operation was well successed
        return attrs[self.__pk]

    def update(self, obj):
        """Update object information in file."""
        # Get objects attributes as {attribute_name: value}
        attrs = self.__get_attr()

        # Create a tuple of all properties
        data = tuple(attrs.values())

        pass

    def delete(self, obj):
        pass

    @classmethod
    def select(cls, **kwargs):
        pass

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

        super().__init__(self.__table, self.__fmt)

        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)

