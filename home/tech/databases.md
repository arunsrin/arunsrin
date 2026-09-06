---
title: "Databases"
tags:
  - databases
  - sql
---

# :material-database:{ .anim-flip } Databases

[Elastic](elastic.md) notes are in a sibling page.

## Notes from "SQL QuickStart Guide"

Author: Walter Shields

### Basic operations

```sql
-- Single line comment
/* Multi 
Line
Comment */
SELECT FirstName, LastName, Email, City from customers;
```

Once more, using aliases:

```sql
SELECT FirstName AS "First Name", LastName AS "Surname", Email, City
from customers;
```

And again, with sorting:

```sql
SELECT FirstName AS "First Name", LastName AS "Surname", Email, City
from customers
ORDER BY Surname DESC;
```

Show only first 10 records: use the keyword `LIMIT`.

### Intermediate operations

/Operators/ are used with other clauses like `SELECT` and `WHERE`. Examples:

- Comparison operators like `=`, `>`, `<=` or `<>`
- Logical operators: `BETWEEN`, `IN`, `LIKE`, `AND`, `OR`
- Arithmetic operators like `+`, `-`, `/`, `*` and `%`

```sql
SELECT
	Total AS [Original Amount],
	Total + 10 AS [Addition example],
	Total - 10 AS [Subtraction example]
FROM
	invoices
ORDER BY
	Total DESC;
```

#### Filtering with `WHERE`:

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE Total = 1.98
ORDER BY InvoiceDate;
```

`WHERE` always comes after the `FROM` but before the `ORDER BY`.

`BETWEEN` gives a range, e.g. `WHERE Total BETWEEN 1.98 AND 5.00`

#### Searching in text:

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE BillingCity IN ('Tucson', 'Paris', 'London')
ORDER BY Total
```

#### Wildcard search with LIKE

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE BillingCity LIKE 'T%'
ORDER BY Total
```

(You can do a `NOT LIKE 'T%'` to invert the results)

#### Filtering by date

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE InvoiceDate = '2009-01-03 00:00:00'
ORDER BY Total
```

#### Something more interesting:

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE InvoiceDate BETWEEN '2009-01-01 00:00:00' AND '2009-12-31 23:59:59'
ORDER BY InvoiceDate
```

#### Using the Date() function

Let's you skip the time, for instance.

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE DATE(InvoiceDate) = '2009-01-03'
ORDER BY Total
```

#### Multiple AND/OR:

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE BillingCity LIKE 'p%' OR BillingCity LIKE 'd%'
ORDER BY Total
```

#### Specifying order:

```sql
SELECT InvoiceDate, BillingAddress, BillingCity, Total
FROM invoices
WHERE Total > 1.98 AND (BillingCity LIKE 'p%' OR
	BillingCity LIKE 'd%')
ORDER BY Total
```

#### The CASE operator

Lets you create a new, temporary field based on some conditions.

```sql
SELECT
	InvoiceDate,
	BillingAddress,
	BillingCity,
	Total,
	CASE
	WHEN TOTAL < 2.00 THEN 'Baseline Purchase'
	WHEN TOTAL BETWEEN 2.00 AND 6.99 THEN 'Low Purchase'
	WHEN TOTAL BETWEEN 7.00 AND 15.00 THEN 'Target Purchase'
	ELSE 'Top Performers'
	END AS PurchaseType
FROM
	invoices
ORDER BY
	BillingCity
```

- Wrapped with `CASE` and `END`
- Alias using `AS` to create the new label
- `WHEN` and `ELSE` to specify the conditions

Now to filter only top performers in the above case, it is trivial to add a
`WHERE PurchaseType = 'Top Performers'` to the query.

### Working with multiple tables

Example of a `JOIN` clause:

```sql
SELECT *
FROM invoices
INNER JOIN customers
ON invoices.CustomerId = customers.CustomerId
```

Here the CustomerId column in customers table is a primary key, while CustomerId in invoices is a
foreign key.

With an alias this time:

```sql
SELECT c.FirstName, c.LastName, i.InvoiceId, i.InvoiceDate, i.Total
FROM invoices as i
INNER JOIN customers as C
ON i.CustomerId = c.CustomerId
ORDER BY c.LastName
```

INNER JOIN shows the intersection of 2 tables. Any info in one table that is missing in the other is
just ignored.

#### LEFT OUTER JOIN

Combines all records in left with matching ones in right. Example:

```sql
SELECT *
FROM invocies AS i
LEFT OUTER JOIN customers AS c
ON i.CustomerId = c.CustomerId
```

SQLite will insert `NULL` data when there are no matching records in the right table.

#### RIGHT OUTER JOIN

Same as LEFT, as you'd expect.

#### Joining more than 2 tables

Example:

```sql
SELECT e.FirstName AS EmpFirstName, e.LastName AS EmpLastName, e.EmployeeId, c.FirstName AS CustomerFirstName, c.LastName AS CustomerLastName, c.SupportRepId, i.CustomerId, i.Total
FROM invoices as i
INNER JOIN customers as c
ON i.CustomerId = c.CustomerId
INNER JOIN employees as e
ON c.SupportRepId = e.EmployeeId
ORDER BY i.Total DESC
LIMIT 10
```

#### Using NULL, IS and NOT

Example: show all artists that do not have a corresponding entry in the album table:

```sql
SELECT 
	ar.ArtistId AS [ArtistId from Artists table],
	al.ArtistId AS [ArtistId from Albums table],
	ar.Name AS [Artist Name],
	al.Title AS [Album]
FROM artists AS ar
LEFT OUTER JOIN albums AS al
ON ar.ArtistId = al.ArtistId
WHERE al.ArtistId IS NULL
```

### Using Functions

Example: Counting occurrences:

```sql
SELECT COUNT(LastName) AS [Name Count]
FROM customers
WHERE LastName LIKE 'B%'
```

#### Types of Functions

- String: INSTR(), LENGTH(), LOWER(), LTRIM(), REPLACE(), RTRIM(), SUBSTR(), TRIM(), UPPER()
- Date: DATE(), DATETIME(), JULIANDAY(), STRFTIME(), TIME(), 'NOW'
- Aggregate: AVG(), COUNT(), MAX(), MIN(), SUM()

#### String manipulation

Adds a space followed by LastName to FirstName:

```sql
SELECT FirstName || ' ' || LastName AS [Full Name]
etc.
```

Substring example, take first five chars of PostalCode:

```sql
SELECT PostalCode, SUBSTR(PostalCode,1,5) AS [Five-digit Postal]
etc.
```

#### Arguments for STRFTIME

- `'%d'` - day of month: 00
- `'%f'` - fractional seconds: SS.SSS
- `'%H'` - hour: 00-24
- `'%j'` - day of year 001-366
- `'%J'` - Julian day number
- `'%m'` - month: 01-12
- `'%M'` - minute: 00-59
- `'%s'` - seconds since 1970-01-01
- `'%S'` - seconds: 00-59
- `'%w'` - day of week: 0-6 (Sunday is 0)
- `'%W'` - week of year: 00-53
- `'%Y'` - year: 0000-9999

Timestrings:

- `'YYY-MM-DD'` - A date typed in Year-Month-Day format
- `'now'` - Current date and time
- `'DATETIME' field` - A databse field in a date and/or time format


Modifiers:

- `'+ X days'` - Add X days to the result
- Same as above for `months` and `years`, and `-` instead of `+`
- `'start of the day'` - modifies the time code to represent the beginning of the day
- Same as above for `month` and `year`

Examples:

```sql
SELECT 
STRFTIME('The year is %Y and day is %d and month is %m', 'now')
AS [Text with Conversion specifications]
```

Example to calculate age:

```sql
SELECT 
	LastName,
	FirstName,
	STRFTIME('%Y-%m-%d', BirthDate) AS [Birthday No Timecode],
	STRFTIME('%Y-%m-%d','now') - STRFTIME('%Y-%m-%d',BirthDate) AS [Age]
FROM employees
ORDER BY Age
```
#### Aggregations

Main ones are SUM(), AVG(), MIN(), MAX(), COUNT().

Example:

```sql
SELECT
	SUM(Total) AS TotalSales,
	AVG(Total) AS AverageSales,
	ROUND(AVG(Total), 2) AS RoundedAverageSales,
	MAX(Total) AS MaxSale,
	MIN(Total) AS MinSale,
	COUNT(*) AS SalesCount
FROM invoices
```

The `*` in `COUNT(*)` ensures that all values are counted, even records with errors or nulls.

Grouping Aggregates:

```sql
SELECT
	BillingCity,
	AVG(Total)
FROM invoices
GROUP BY BillingCity
ORDER BY BillingCity
```
Run this without GROUP BY and you will see that the response is messed up, i.e. it tries to print
the BillingCity which is a multi-line reponse, and also the AVG(Total) which is a single row.

#### Filtering based on Aggregates with HAVING

`WHERE` does not work with functions. So if you want to show only rows where AVG exceeds 6, use `HAVING`:

```sql
SELECT
	BillingCity,
	AVG(Total)
FROM invoices
GROUP BY BillingCity
HAVING AVG(Total) > 6
ORDER BY BillingCity
```

`HAVING` always comes after the `GROUP BY` clause.

The `WHERE` clause tells SQL what data to include in the table. Once the information is filtered and
aggregate functions are applied, `HAVING` acts as a further filter.

### Subqueries

Basically, one query inside another.

Example: Find the Average of sales, and find all rows that were below this average. Since we can't
use `WHERE` when you're using an aggregate function, you'd have to make a subquery and embed it in
another. Example:

```sql
SELECT
	InvoiceDate,
	BillingAddress,
	BillingCity,
	Total
FROM invoices
WHERE Total < 
(select 
	AVG(Total)
from invoices)
ORDER BY Total DESC)
```

Another example, in a `SELECT` statement:

```sql
SELECT
	BillingCity,
	AVG(Total) AS [City Average],
	(select
		avg(total)
	from
		invoices) AS [Global Average]
FROM invoices
GROUP BY BillingCity
ORDER BY BillingCity
```

Another, in a `WHERE` clause, in this case we want to see which sales in 2014
has beaten 2013's highest sale.

```sql
SELECT
	InvoiceDate,
	BillingCity,
	Total
FROM
	invoices
WHERE
	InvoiceDate >= '2013-01-01' AND total > 
	(select
		max(Total)
	from invoices
	where InvoiceDate < '2013-01-01')
```

Here's one where we're interested in 3 invoces. We write a query to extract the
dates they were purchased. Then we pipe that into another query and see all
sales that happened in those dates.

```sql
SELECT
	InvoiceDate,
	BillingAddress,
	BillingCity
FROM invoices
WHERE InvoiceDate IN
	(select InvoiceDate
	from invoices
	where InvoiceId in (251,252,255))
```
#### DISTINCT

Here we want all tracks that do not appear in invoice_items i.e have never been
bought. This is the query:

```sql
select Name, composer from tracks where trackid not in
(select DISTINCT TrackId from invoice_items)
```

Note that without the `DISTINCT` keyword, we would get a large result with lots
of repetitions. So this is the equivalent of doing a `set(some_list)` in
python.

### Views

A virtual table that's basically a stored query that can be executed/references
by other queries.

Prefix a statement with `CREAE VIEW <blah> AS` to make one. Example:

```sql
CREATE VIEW V_AvgTotal AS
SELECT
	ROUND(AVG(Total), 2) AS [Average Total]
FROM invoices
```

Naming with a `V_` prefix is a good convention to follow.

Another example for a joined query:

```sql
CREATE VIEW V_Tracks_InvoiceItems AS
SELECT
	ii.InvoiceId,
	ii.UnitPrice,
	ii.Quantity,
	t.Name,
	t.Composer,
	t.Milliseconds
FROM
	invoice_items ii
INNER JOIN
	tracks t
ON ii.TrackId = t.Trackid
```
Now you can use this in some other query.

To remove it:

```sql
DROP VIEW V_Tracks_InvoiceItems
```
No data is deleted, just the view is removed.

### DML (Data Manipulation Language)

This is about inserting/updating/deleting data. Simplest example:

```sql
INSERT INTO artists (Name)
VALUES ('Bob Marley')
```

Simple UPDATE:

```sql
UPDATE employees SET PostalCode = '11202'
WHERE EmployeeId = 9
```
And DELETE:

```sql
DELETE FROM employees WHERE EmployeeId = 9
```

## Cassandra quickstart

I'm actually using ScyllaDB which is compatible with Cassandra.

`cqlsh` is it's shell.

``` sql
DESCRIBE keyspaces;
USE <name-of-keyspace>;
DESCRIBE tables;
SELECT * FROM <name-of-table>;
```

## PostgreSQL quickstart

``` sql
sudo -i -u postgres
psql
# Inside psql:
# CREATE DATABASE ttrssdb;
# CREATE USER ttrssuser WITH ENCRYPTED PASSWORD 'blah';
# GRANT ALL PRIVILEGES ON DATABASE ttrssdb TO ttrssuser;
```

## MySQL / MariaDB quick start

Modern MySQL/MariaDB prefers creating the user first, then granting permissions.

``` sql
mysql> CREATE DATABASE habari;
mysql> CREATE USER 'habariuser'@'localhost' IDENTIFIED BY 'blah';
mysql> GRANT ALL PRIVILEGES ON habari.* TO 'habariuser'@'localhost';
mysql> FLUSH PRIVILEGES;
```

## Sqlite basics:

``` sql
thaum ~/code/app$ sqlite perl.db
SQLite version 2.8.17
Enter ".help" for instructions
sqlite> .tables
sqlite> .schema
sqlite> create table perltest (id integer PRIMARY KEY,name varchar(10), salary integer);
sqlite> .tables
perltest
sqlite> .headers on
sqlite> .mode column
sqlite> select * from perltest;
sqlite> insert into perltest values(1,'arun',12345);
sqlite> insert into perltest values(2,'brun',23456);
sqlite> select * from perltest;
id          name        salary
----------  ----------  ----------
1           arun        12345
2           brun        23456
```


