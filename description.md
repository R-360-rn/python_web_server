Requirements: Python 3.6+

Create a simple http server that provides two services:

 

Service 1: Should accept GET requests to the root path (/) with 3 parameters: 'a', 'b' and 'op'. 'a' and 'b' are numbers and 'op' is one of the following characters: "-", "/", "*" or "%2b" (uri encoded "+").

Server should return JSON response with status, result of the specified operation and current date and time.

 

Example:

curl "http://localhost:8000/?a=340.234&b=450000000&op=*"
{
  "status": "ok",
  "date": "2021-04-22 16:31",
  "result": 153105300000.0
}
 

Server should be able to handle wrong input, absence of parameters in query and respond with correct HTTP codes, for example:

 
curl -v "http://localhost:8000/?b=450000000&op=*"
*   Trying 127.0.0.1:8000...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET /?b=450000000&op=* HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 400 Bad Request
< Server: SimpleHTTP/0.6 Python/3.8.5
< Date: Thu, 22 Apr 2021 14:36:10 GMT
< Content-type: application/json
< 
{
  "status": "error",
  "reason": "a not found in query string"
}
 

Service 2: Server should have an sqlite3 database with a table that contains the following fields:

 
id - integer, autoincrement, mandatory
name - text, mandatory,
address - text, length 100,
salary - float,
age - integer, mandatory
 

and serve one endpoint at path /users/ with two methods: GET and POST.

 

POST: Post method should accept json encoded data, check it's validity, ensure all mandatory parameters are provided, and save them to the database. Additionally server should verify that name is unique, otherwise (the same name has been already in the database) it should return an error.
Once a record created in the database the server should throw a response containing all the fields from the record.

Happy path example:

curl -X POST http://127.0.0.1:8000/users/ -d '{ "name": "John", "address": "Praha, 15000", "age": 18, "salary": 0 }'{
  "status": "success",
  "result": {
    "id": 1,
    "name": "John",
    "age": 18,
    "salary": 0.0,
    "address": "Praha, 15000"
  },
  "date": "2021-04-23 12:02:56"
}
Example for the case when provided name is not unique:

{
  "status": "error",
  "reason": "User with such name is already present"
}
 

GET: Get method should accept "id" and/or "name". Server should check database and return json encoded object or 404 if relevant record was not found.

Happy path example:

curl http://127.0.0.1:8000/users/?id=1
{
  "status": "success",
  "result": {
    "id": 1,
    "name": "John",
    "age": 18,
    "salary": 0.0,
    "address": "Praha, 15000"
  },
  "date": "2021-04-23 12:17:24"
}
Example for the case when record is not found:

curl "http://127.0.0.1:8000/users/?id=1&name=Smith"
{
  "status": "error",
  "reason": "Requested user not found"
}
Example for invalid query:

curl "http://127.0.0.1:8000/users/"
{
  "status": "error",
  "reason": "id or name is required"
}
Everything should be wrapped into a docker container.