import argparse
from math import fsum
from src.pysort import timsort
from src.helper import to_str, to_date
from src.pydata import Department, Subdepartment, Employee, Transaction


def load(filepath):
    """Load data on filepath to database."""
    # Columns: 5, 12, 15, 17, 23, 25
    # Names: employee name, subdepartment, description, date, value, department
    # Mapping to right column index
    cols = {
        'department': 25, 'subdepartment': 12, 'date': 17,
        'employee': 5, 'description': 15, 'value': 23
    }

    n = 0

    # Load data
    file = open(filepath, 'r')
    file.readline()

    line = file.readline()

    while line:
        data = line.split(';')

        # Save deparment
        dep_name = to_str(data[cols['department']])
        department = Department.select(name=dep_name)

        if len(department):
            department = department[0]
        else:
            department = Department(name=dep_name)
            department.save()

        # Save subdepartment
        subdep_name = to_str(data[cols['subdepartment']])
        subdepartment = Subdepartment.select(name=subdep_name)

        if len(subdepartment):
            subdepartment = subdepartment[0]
        else:
            subdepartment = Subdepartment(name=subdep_name, department_id=department.id)
            subdepartment.save()

        # Save employee
        employee_name = to_str(data[cols['employee']])
        employee = Employee.select(name=employee_name)

        if len(employee):
            employee = employee[0]
        else:
            employee = Employee(name=employee_name, subdepartment_id=subdepartment.id)
            employee.save()

        # Save trenasaction
        description = to_str(data[cols['description']])
        value = float(data[cols['value']].replace(',', '.'))
        date = to_date(data[cols['date']])

        transaction = Transaction.select(employee_id=employee.id, description=description)

        if not len(transaction):
            transaction = Transaction()

            transaction.employee_id = employee.id
            transaction.description = description
            transaction.value = value
            transaction.date = date

            transaction.save()

        n = n + 1
        line = file.readline()

    file.close()

    print("{} transactions saved.".format(n))


def delete(args):
    """Delete a registry from DB."""
    e_name = args.d_entity.capitalize()
    entity = eval('{}.get({})'.format(e_name, args.id))

    if entity:
        print(str(entity))
        entity.delete()
    else:
        print("{} with ID {} does not exist.".format(e_name, args.id))


def update(args):
    """Update a registry from DB."""
    e_name = args.u_entity.capitalize()
    entity = eval('{}.get({})'.format(e_name, args.id))

    print(str(entity))
    print('-' * 80)

    if args.name:
        entity.name = to_str(args.name)

    if args.department_id:
        entity.department_id = args.department_id

    if args.subdepartment_id:
        entity.subdepartment_id = args.subdepartment_id

    if args.employee_id:
        entity.employee_id = args.employee_id

    if args.description:
        entity.description = to_str(args.description)

    if args.value:
        entity.value = float(args.value)

    if args.date:
        entity.date = to_date(args.date)

    entity.update()
    print(str(entity))


def search(args):
    """Search a registry by name or ids."""
    e_name = args.s_entity.capitalize()

    if args.id:
        results = [eval('{}.get(int(args.id))'.format(e_name))]
    else:
        kwargs = dict()

        kwargs['name'] = to_str(args.name)
        kwargs['dep_id'] = args.department_id
        kwargs['subdep_id'] = args.subdepartment_id
        kwargs['employee_id'] = args.employee_id
        kwargs['description'] = to_str(args.description)

        results = eval('{}.select(**kwargs)'.format(e_name))

    if results:
        print('{} record(s) found.\n'.format(len(results)))

        for obj in results:
            print(str(obj))
            print('-' * 80)
    else:
        print('Nothing was found.')


def sort(args):
    """Sort records of an entity."""
    e_name = args.o_entity.capitalize()
    records = eval(e_name + '.all()')

    key = lambda x: eval('x.' + args.key)
    records = timsort(records, key=key)

    if args.reversed:
        records = list(reversed(records))

    for r in records:
        print(repr(r))


def report(args):
    eval(args.report + '(args)')


def employee_expenses(args):
    if args.id:
        employee = [Employee.get(int(args.id))]
    else:
        employee = Employee.select(name=args.name)

    print('{} record(s) found.'.format(len(employee)))

    for e in employee:
        transactions = Transaction.select(employee_id=e.id)

        total = [t.value for t in transactions]
        total = fsum(total)

        print()
        print(str(e))
        print('TOTAL: R$ {:,.2f}'.format(total))
        print('-' * 80)

        if args.detailed:
            for t in transactions:
                str_t = str(t).replace('\n', '\n\t\t')
                print('\t\t{}'.format(str_t))
                print('-' * 80)


def department_expenses(args):
    if args.id:
        department = [Department.get(int(args.id))]
    else:
        department = Department.select(name=args.name)

    print('{} record(s) found.'.format(len(department)))

    for d in department:
        transactions = Transaction.select(dep_id=d.id)

        total = [t.value for t in transactions]
        total = fsum(total)

        print()
        print(str(d))
        print('TOTAL: R$ {:,.2f}'.format(total))
        print('-' * 80)

        if args.detailed:
            for t in transactions:
                str_t = str(t).replace('\n', '\n\t\t')
                print('\t\t{}'.format(str_t))
                print('-' * 80)


def expensive_employee(args):
    transactions = Transaction.select(year=int(args.year))
    employees = Employee.all()

    most_expensive = list([-1])
    most_total = list([-1])

    for e in employees:
        employee_t = filter(lambda x: x.employee_id == e.id, transactions)
        employee_t = list(employee_t)

        total = [t.value for t in employee_t]
        total = fsum(total)

        if total > most_total[-1]:
            most_expensive = list()
            most_total = list()

            most_expensive.append(e)
            most_total.append(total)
        elif total == most_total[-1]:
            most_expensive.append(e)
            most_total.append(total)

    for e, t in zip(most_expensive, most_total):
        print(str(e))
        print('TOTAL: R$ {:,.2f}'.format(t))
        print('-' * 80)


def expensive_department(args):
    transactions = Transaction.select(year=int(args.year))
    departments = Department.all()

    most_expensive = list([-1])
    most_total = list([-1])

    for e in departments:
        dep_trans = Transaction.select(dep_id=e.id, field=1)

        employee_t = filter(lambda x: x.employee_id in dep_trans, transactions)
        employee_t = list(employee_t)

        total = [t.value for t in employee_t]
        total = fsum(total)

        if total > most_total[-1]:
            most_expensive = list()
            most_total = list()

            most_expensive.append(e)
            most_total.append(total)
        elif total == most_total[-1]:
            most_expensive.append(e)
            most_total.append(total)

    for e, t in zip(most_expensive, most_total):
        print(str(e))
        print('TOTAL: R$ {:,.2f}'.format(t))
        print('-' * 80)

def cheapest_employee(args):
    transactions = Transaction.select(year=int(args.year))
    employees = Employee.all()

    most_expensive = list([])
    most_total = list([100000000000])

    for e in employees:
        employee_t = filter(lambda x: x.employee_id == e.id, transactions)
        employee_t = list(employee_t)

        total = [t.value for t in employee_t]
        total = fsum(total)

        if total > 0:
            if total < most_total[-1]:
                most_expensive = list()
                most_total = list()

                most_expensive.append(e)
                most_total.append(total)
            elif total == most_total[-1]:
                most_expensive.append(e)
                most_total.append(total)

    for e, t in zip(most_expensive, most_total):
        print(str(e))
        print('TOTAL: R$ {:,.2f}'.format(t))
        print('-' * 80)


def cheapest_department(args):
    transactions = Transaction.select(year=int(args.year))
    departments = Department.all()

    most_expensive = list([])
    most_total = list([100000000000])

    for e in departments:
        dep_trans = Transaction.select(dep_id=e.id, field=1)

        employee_t = filter(lambda x: x.employee_id in dep_trans, transactions)
        employee_t = list(employee_t)

        total = [t.value for t in employee_t]
        total = fsum(total)

        if total > 0:
            if total < most_total[-1]:
                most_expensive = list()
                most_total = list()

                most_expensive.append(e)
                most_total.append(total)
            elif total == most_total[-1]:
                most_expensive.append(e)
                most_total.append(total)

    for e, t in zip(most_expensive, most_total):
        print(str(e))
        print('TOTAL: R$ {:,.2f}'.format(t))
        print('-' * 80)


def total_expenses(args):
    transactions = Transaction.select(year=int(args.year), field=3)
    total = fsum(transactions)

    print('-' * 80)
    print('TOTAL FOR {}: R$ {:,.2f}'.format(args.year, total))
    print('-' * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Load params
    parser.add_argument("-l", "--load",
                        dest="filepath",
                        default=None,
                        help="Load data on filepath to database.")

    # Delete params
    parser.add_argument("-p", "--delete",
                        dest="d_entity",
                        default=None,
                        help="Entity to delete.")

    parser.add_argument("-c", "--id",
                        dest="id",
                        default=None,
                        help="Entity's id.")

    # Update params
    parser.add_argument("-u", "--update",
                        dest="u_entity",
                        default=None,
                        help="Entity to update.")

    parser.add_argument("-n", "--name",
                        dest="name",
                        default='',
                        help="Entity's name.")

    parser.add_argument("-a", "--department_id",
                        dest="department_id",
                        default=None,
                        help="Entity's department id.")

    parser.add_argument("-s", "--subdepartment_id",
                        dest="subdepartment_id",
                        default=None,
                        help="Entity's subdepartment id.")

    parser.add_argument("-e", "--employee_id",
                        dest="employee_id",
                        default=None,
                        help="Entity's employee id.")

    parser.add_argument("-d", "--description",
                        dest="description",
                        default='',
                        help="Entity's description.")

    parser.add_argument("-v", "--value",
                        dest="value",
                        default=None,
                        help="Entity's value.")

    parser.add_argument("-t", "--date",
                        dest="date",
                        default=None,
                        help="Entity's date as YYYY-MM-DD.")

    # Search params
    parser.add_argument("-f", "--search",
                        dest="s_entity",
                        default=None,
                        help="Entity to be searched.")

    # Sort params
    parser.add_argument("-o", "--sort",
                        dest="o_entity",
                        default=None,
                        help="Entity to be sorted.")

    parser.add_argument("-i", "--reversed",
                        dest="reversed",
                        default=False,
                        help="Reversed sorted.")

    parser.add_argument("-k", "--key",
                        dest="key",
                        default='id',
                        help="Key to use in sort.")

    # Report params
    parser.add_argument("-r", "--report",
                        dest="report",
                        default=None,
                        choices=[
                                    'employee_expenses',
                                    'department_expenses',
                                    'expensive_employee',
                                    'expensive_department',
                                    'cheapest_employee',
                                    'cheapest_department',
                                    'total_expenses'
                                ],
                        help="Report type.")

    parser.add_argument("-b", "--detailed",
                        dest="detailed",
                        default=False,
                        help="Show report details.")

    parser.add_argument("-year", "--year",
                        dest="year",
                        default=None,
                        help="Show report details.")

    args = parser.parse_args()

    if args.filepath:
        load(args.filepath)

    if args.d_entity:
        delete(args)

    if args.u_entity:
        update(args)

    if args.s_entity:
        search(args)

    if args.o_entity:
        sort(args)

    if args.report:
        report(args)
