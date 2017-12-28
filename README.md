# Inquiry of Public Expenses of the city of Porto Alegre

This project was idealized for *Classificação e Pesquisa de Dados*, Computer Science undergraduation program's subject of *Federal University of Rio Grande do Sul (UFRGS)*.

This implementation of database concepts uses data from http://datapoa.com.br/dataset/despesas-com-diarias.

## Data Structure

**Department**
- id: unique code
- name: department's name
---
**Subdepartment**
- id: unique code
- name: subdepartment's name
- department_id: a *Department* unique code
---
**Employee**
- id: unique code
- name: employee's name
- subdepartment_id: a *Subdepartment* unique code
---
**Transaction**
- id: unique code
- employee_id: a *Employee* unique code
- description: transaction's description
- value: transaction's value (R$)
- date: transaction's timestamp

## Command Line Methods

### Load
```bash
$ python3 main.py --load data/expenses_2014.csv
```
The `--load` flag loads the data from a .CSV file to database (data's binary representation).

### Delete\*
```bash
$ python3 main.py --delete employee --id 10
```
The command above deletes an employee with unique code equals to 10.
\**This method also deletes all related data.*

### Update
```bash
$ python3 main.py --update department --id 5 --name Secretaria de Saúde
```
This command updates the name of a department record with id 10. According to data structure, you can update any information using the field's flag (ex.: `--value` to update a transaction's value).

### Search
```bash
$ python3 main.py --search transaction --id 154
```
You can search a record of any entity using any field.

### Sort
```bash
$ python3 main.py --sort employee --reversed True --key name
```
Sort employee by name from Z to A (reversed). By default, reversed is False and key is id.

### Report
```bash
$ python3 main.py --report <report_type> --<field> <field_value> --detailed True
```
**Report Types...**
- **... that support {id, name} as fields:**
    - employee_expenses: show employee's transactions
    - department_expenses: show department's transactions
- **... that support {year} as field:**
    - expensive_employee: show employee with the biggest account in *\<year\>*
    - expensive_department: show department with the biggest account in *\<year\>*
    - cheapest_employee: show employee with the smallest account in *\<year\>*
    - cheapest_department: show department with the smallest account in *\<year\>*
    - total_expenses: show sum of all expenses in *\<year\>*
---
**Example**
```bash
$ python3 main.py --report employee_expenses --name Fogaça
```
This command shows total expenses by employee that has *Fogaça* in name. By default, detailed is set to False. When True, show all transactions.
---
```bash
$ python3 main.py --report total_expenses --year 2010
```
To see the total of public expenses in 2010.
