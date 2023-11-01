# NoSQL Databases with MongoDB

**FastAPI** can also be integrated with <abbr title="Distributed database (Big Data), also 'Not Only SQL'">NoSQL</abbr> databases.

Here we'll see an example using **<a href="https://www.mongodb.com/" class="external-link" target="_blank">MongoDB</a>**, a <abbr title="Document here refers to a JSON object (a dict), with keys and values, and those values can also be other JSON objects, arrays (lists), numbers, strings, booleans, etc.">document</abbr>-based NoSQL database.

!!! tip
    There is an official full-stack project generator with **FastAPI**, **MongoDB**, and **React/Redux**, all containerized with **Docker**: <a href="https://github.com/Jibola/farm-stack-generator" class="external-link" target="_blank">https://github.com/Jibola/farm-stack-generator</a>

## Asynchronous Python
This guide uses `async/await`, which allows us to write concurrent, non-blocking code. If you're unfamiliar with asynchronous Python, the **<a href="https://fastapi.tiangolo.com/async/" class="internal-link" target="_blank">FastAPI async docs</a>** are a good start. 

## Dependency installation
We'll be using two other dependencies besides **FastAPI**: **<a href="https://beanie-odm.dev/" class="external-link" target="_blank">Beanie</a>** and **<a href="https://motor.readthedocs.io/en/stable/" class="external-link" target="_blank">Motor</a>**. 

Install **Beanie** with

```Python
python -m pip install beanie
```

And install **Motor** with

```Python
python -m pip install "motor[snappy,gssapi,srv,tls]"
```

If you are on macOS using Apple Silicon, you will need to first run `brew install snappy` and use this to install **Motor** instead:

```Python
CPPFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" python -m pip install "motor[snappy,gssapi,srv,tls]"
```

## Introduction to MongoDB

**MongoDB** uses a <abbr title="Document here refers to a JSON object (a dict), with keys and values, and those values can also be other JSON objects, arrays (lists), numbers, strings, booleans, etc.">document</abbr>-based data model, meaning data is stored as JSON objects instead of rows inside the database. Data is organized into collections of documents, similar to tables in a relational database. A single MongoDB instance can have many databases, each containing one or more collections.  

### Getting started with MongoDB Atlas

First, we need to create a **MongoDB** server to store our data. We'll use a **<a href="https://www.mongodb.com/docs/atlas/" class="external-link" target="_blank">MongoDB Atlas</a>** free cluster, a cloud-hosted option for **MongoDB**.  

To do so, follow the **<a href="https://www.mongodb.com/docs/atlas/getting-started/#get-started-with-atlas" class="external-link" target="_blank">Get Started with Atlas</a>** guide up to **step 5, Connect to your cluster.** Then, follow the instructions <a href="https://www.mongodb.com/docs/manual/reference/connection-string/#find-your-mongodb-atlas-connection-string" class="external-link" target="_blank">here</a> to get your Atlas connection string.

Then, create a `AsyncIOMotorClient` and pass your connection string to its constructor:

```Python hl_lines="8-10"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

You're all set to start using **MongoDB**!

### Connection management

It's important to note that we've created our `AsyncIOMotorClient` at the top level of our application, ensuring that there's only **MongoDB** client shared among all connections. Each client creates a separate connection to the underlying **MongoDB** database, which can harm performance if done unnecessarily. Most applications only require a single **MongoDB** client, which can handle many different connections and queries to the database over the course of an application's operation.

## Create a Beanie Document

Since **MongoDB** stores data as JSON objects, we can model our data using the **Beanie** `Document` class.

The `Document` class maps a Python class to a **MongoDB** document schema, allowing us to easily perform operations on our data using structured Python objects.

Our simple Beanie `Document` is `User`, representing a user's information in the database:

```Python hl_lines="13-16"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

You can create data using our `User` class like this:

```Python
user = User(username="bsmith", email="bobsmith@example.com", full_name="Bob Smith")
```

Using our **Beanie** `Document`, data in our **MongoDB** collection will look something like this:

```Python
{
    "username": "bsmith"
    "email": "bobsmith@example.com"
    "full_name": "Bob Smith"
}
```

For more information on **Beanie** `Document`s, refer to the official <a href="https://beanie-odm.dev/tutorial/defining-a-document/" class="external-link" target="_blank">**Beanie docs**</a>.

## Configure Beanie

Now that we've created our `User` class, we need to tell **Beanie** that we want to use it to structure our data. To do so, we need to call the asynchronous `init_beanie` function and pass the **MongoDB** database and document models we want to use: 

```Python hl_lines="26-27"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

As you can see by the use of `client.database_name` above, databases are accessed as attributes of `AsyncIOMotorClient`. If the specified database does not already exist, **Motor** will automatically create it for you.

By default, **Beanie** will automatically name our collection after the name of our `Document`, which will be `user` in this case. You can also set the collection name for a `Document` explicitly: refer to the <a href="https://beanie-odm.dev/tutorial/defining-a-document/#collection-name/" class="external-link" target="_blank">**Beanie docs**</a> for instructions on doing so. 

### Initialize Beanie

We need to make sure that **FastAPI** initializes **Beanie** before it starts accepting requests.

We'll do this using <a href="https://fastapi.tiangolo.com/advanced/events/#lifespan-events" class="internal-link" target="_blank">**lifespan events**</a>. Lifespan events allow us to define code that will be run once before our application starts up, and code that will be run once after our application shuts down. 

Here's what our lifespan hook looks like:

```Python hl_lines="30-33"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

We call our `init_db` method from before and `await` it, ensuring that the setup actually completes before we give control back to the application. Anything after `yield` statement would be run on application shutdown: since we don't need to do anything to spin down **Beanie**, we can leave that blank.

Now that we've created our lifespan event handler, we just need to pass it to our **FastAPI** constructor:

```Python hl_lines="36"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

Now we've set up our connection to **MongoDB** and configured **Beanie** and **FastAPI**, leaving us with creating our API endpoints.

## Fetch a user

Next, we'll create a function to fetch a user from the database, using a given username:

```Python hl_lines="19-23"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

**Beanie**'s `Document.find_one` method gets a single **MongoDB** document from the given `Document`'s collection that matches the given filter, if such a document exists. If no match is found, it will return `None`. To handle that case, we raise a `404 Not Found` exception that **FastAPI** will send back as a response, notifying the end user.

We want to separate our **FastAPI**-interacting code from our **MongoDB**-interacting code to allow for easy reuse and <abbr title="Automated test, written in code, that checks if another piece of code is working correctly.">unit tests</abbr>. This way, if our API endpoints change or have additional functionality added, we don't necessarily need to modify our `fetch_user` function.

## Create your **FastAPI** code

Finally, we need to create the **FastAPI** component of our application. Doing so requires two steps: creating an instance of `FastAPI`, and defining API endpoints for users to interact with.

We already created our `FastAPI` instance when we configured **Beanie**, which leaves just our API endpoints.

We'll need two endpoints: one for saving a new user to the database, and one for retrieving a user by username

### Save a user to the database

Saving a user to the database is simple thanks to **Beanie**'s `Document.insert`:

```Python hl_lines="39-48"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

This waits for **Beanie** to insert the request's `User` to the database, and then returns the successfully inserted data. Any error will be caught and returned back to the user as the response.

### Get a user from the database

Getting a user by username is equally simple:

```Python hl_lines="51-65"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

We call our abstracted `fetch_user` method from earlier, passing in the supplied username to search for. A successful match in the database will return the found user, while an error will return a response.

## Conclusion

Congratulations, you've created a simple **MongoDB** + **FastAPI** application! You can start it up by following the same steps as in the **<a href="https://fastapi.tiangolo.com/tutorial/first-steps/" class="internal-link" target="_blank">First steps</a>** guide.

For examples of more complex functionality, a good place to start is the official documentation for **<a href="https://beanie-odm.dev/" class="external-link" target="_blank">Beanie</a>** and **<a href="https://motor.readthedocs.io/en/stable/" class="external-link" target="_blank">Motor</a>**.
