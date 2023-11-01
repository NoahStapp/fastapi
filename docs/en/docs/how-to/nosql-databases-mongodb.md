# NoSQL Databases with MongoDB

**FastAPI** can also be integrated with <abbr title="Distributed database (Big Data), also 'Not Only SQL'">NoSQL</abbr> databases.

Here we'll see an example using **<a href="https://www.mongodb.com/" class="external-link" target="_blank">MongoDB</a>**, a <abbr title="Document here refers to a JSON object (a dict), with keys and values, and those values can also be other JSON objects, arrays (lists), numbers, strings, booleans, etc.">document</abbr>-based NoSQL database.

!!! tip
    There is an official full-stack project generator with **FastAPI**, **MongoDB**, and containerized with **Docker**: <a href="https://github.com/Jibola/farm-stack-generator" class="external-link" target="_blank">https://github.com/Jibola/farm-stack-generator</a>

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

First, we need to create a MongoDB server to store our data. We'll use a **<a href="https://www.mongodb.com/docs/atlas/" class="external-link" target="_blank">MongoDB Atlas</a>** free cluster, a cloud-hosted option for MongoDB.  

To do so, follow the **<a href="https://www.mongodb.com/docs/atlas/getting-started/#get-started-with-atlas" class="external-link" target="_blank">Get Started with Atlas</a>** guide up to **step 5, Connect to your cluster.** Then, follow the instructions <a href="https://www.mongodb.com/docs/manual/reference/connection-string/#find-your-mongodb-atlas-connection-string" class="external-link" target="_blank">here</a> to get your Atlas connection string.

Then, create a `AsyncIOMotorClient` and pass your connection string to its constructor:

```Python hl_lines="8"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

You're all set to start using MongoDB!

## Create a Beanie Document

Since **MongoDB** stores data as JSON objects, we can model our data using the Beanie `Document` class.

The `Document` class maps a Python class to a MongoDB document schema, allowing us to easily perform operations on our data using structured Python objects.

Our simple Beanie `Document` is `User`, representing a user's information in the database:

```Python hl_lines="11-14"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

You can create data using our `User` class like this:

```Python
user = User(username="bsmith", email="bobsmith@example.com", full_name="Bob Smith")
```

Using our Beanie `Document`, data in our MongoDB collection will look something like this:

```Python
{
    "username": "bsmith"
    "email": "bobsmith@example.com"
    "full_name": "Bob Smith"
}
```

By default, **Beanie** will automatically name our collection after the name of our `Document`, which will be `user` in this case.

For more information on Beanie `Document`s, refer to the official <a href="https://beanie-odm.dev/tutorial/defining-a-document/" class="external-link" target="_blank">**Beanie docs**</a>.

## Create an MongoDB client and ODMantic engine

To support the use of models like the one we created above, **ODMantic** uses its own engine to interact with **MongoDB**. There are both synchronous (SyncEngine) and asynchronous (AIOEngine) implementations available in **ODMantic**: for the purposes of this example, we will use SyncEngine. 

When creating an engine, **ODMantic** defaults to MongoDB running on `localhost` port `27017` and uses database `test`. To define your own parameters, you can provide an instance of `MongoClient` (synchronous) or `AsyncIOMotorClient` (asynchronous) to the engine constructor:

```Python hl_lines="8-9"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

Once your engine is created, you can use it to perform operations on your database. For more information on the kinds of operations **ODMantic** engines support, refer to the official <a href="https://art049.github.io/odmantic/engine/" class="external-link" target="_blank">**ODMantic** docs</a>. 

### Connecting to MongoDB

It's important to note that we've created our `MongoClient` and `SyncEngine` at the top level of our application, ensuring that there's only one engine and MongoDB client. Each engine/client creates a separate connection to the underlying MongoDB database, which can harm performance if done unnecessarily. Most applications only require a single **ODMantic** engine and associated MongoDB client.

## Fetch a user

Next, we'll create a function to fetch a user from the database, using a given username:

```Python hl_lines="25-29"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

**ODMantic**'s SyncEngine `find_one` method gets a single **MongoDB** document from the given `Model`'s collection that matches the given filter, if such a document exists. If no match is found, it will return `None`. To handle that case, we raise a `404 Not Found` exception that **FastAPI** will send back as a response, notifying the end user.

We want to separate our **FastAPI**-interacting code from our **MongoDB**-interacting code to allow for easy reuse and <abbr title="Automated test, written in code, that checks if another piece of code is working correctly.">unit tests</abbr>. This way, if our API endpoints change or have additional functionality added, we don't necessarily need to modify our `get_user` function.

## Create your **FastAPI** code
Finally, we need to create the **FastAPI** component of our application. Doing so requires two steps: creating an instance of `FastAPI`, and defining API endpoints for users to interact with.

### Create the `FastAPI` app

First, we create our `FastAPI` instance, which serves as the backend around all of our endpoints.

Doing so is very easy:

```Python hl_lines="46"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

### Define an API endpoint

We will create two endpoints: one for saving a new user to the database, and one for retrieving a user by username.

Saving a user to the database is simple thanks to **ODMantic**'s engine:

```Python hl_lines="29-35"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```

`engine.save` stores the `User` data passed by the request as a document in our **MongoDB** collection. We then return the stored `User` back as the request response.

Our endpoint is very simple, parsing a username given by the request and fetching the API

```Python hl_lines="34-37"
{!../../../docs_src/nosql_databases/tutorial002.py!}
```
