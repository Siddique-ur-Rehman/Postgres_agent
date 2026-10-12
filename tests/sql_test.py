
from sql_tools import execute_sql

result = execute_sql.invoke({
    "query": "SELECT name, marks FROM students ORDER BY marks DESC LIMIT 3"
})

print(result)
