Data Service for World Bank Economic Indicators
=======
The World Bank indicators API provides 50 year of data over more than 1500 indicators for countries around the world.<br>
   * List of indicators can be found at: [http://api.worldbank.org/v2/indicators](http://api.worldbank.org/v2/indicators)
   * List of countries can be found at: [http://api.worldbank.org/v2/countries](http://api.worldbank.org/v2/countries)
---------
Resources:
   * [PyMongo documents](https://api.mongodb.com/python/current/)
   * [Flask-RESTPlus’s documentation](https://flask-restplus.readthedocs.io/en/stable/)

--------
Procedure:
  * Start a virtual environment and install requirements<br>
  * Write app.py which is the API application that will be deployed<br>
  * Configuration pymongo databse which is connected to mlab<br>
  * Update requirements.txt as you write the code<br>
  * Test the API<br>

---------
File Structure
  * app_name<br>
    *       app.py: Flask API application
    *       config.py: configuration pymongo database
    *       requirements.txt: list of packages that the app will import
