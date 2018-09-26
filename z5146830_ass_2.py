from flask import Flask, request
import requests
from flask_restplus import Api, Resource, fields, reqparse
from pymongo import MongoClient
from datetime import datetime
import pprint
from bson import ObjectId
import re


DB_NAME = 'comp9321'
DB_HOST = 'ds155862.mlab.com'
DB_PORT = 55862
DB_USER = 'admin2'
DB_PASS = 'admin3'

client = MongoClient(DB_HOST, DB_PORT)
db = client[DB_NAME]
db.authenticate(DB_USER, DB_PASS)
countries = db['countries']

app = Flask(__name__)
api = Api(app,
          title='WorldBank',
          description='collection will be imported if you input an indicator')

indicator_model = api.model('id', {
    'indicator': fields.String
})

parser = reqparse.RequestParser()
parser.add_argument('q', help=('this is an optional parameter'))


@api.route('/collections')
class Collections(Resource):

    @api.response(404, 'page not found')
    @api.response(201, 'collection is imported successfully')
    @api.response(200, 'collection is imported before')
    @api.expect(indicator_model, validate=True)
    @api.doc(description='import a collection')
    def post(self):
        r = request.json
        id = r["indicator"]
        validate = countries.find_one({'indicator': id})
        if validate:
            return {'message': 'this collection = {} is already exists'.format(id)}, 200
        new_collection = {}
        entry = []
        try:
            for page in range(1, 3):
                response = requests.get(
                     'http://api.worldbank.org/v2/countries/all/indicators/{}?date=2012:2017&format=json&page={}'.\
                         format(id, page))
                data = response.json()
                new_collection["indicator"] = id
                new_collection["indicator_value"] = data[1][0]["indicator"]["value"]
                new_collection["creation_time"] = str(datetime.utcnow())
                for i in data[1]:
                    country = {}
                    country["county"] = i['country']['value']
                    country["date"] = i['date']
                    if not i['value']:
                        country['value'] = -1
                    else:
                        country["value"] = i['value']
                    entry.append(country)
            new_collection["entries"] = entry
            collection_id = countries.insert_one(new_collection).inserted_id
            # pprint.pprint(countries.find_one())
            # pprint.pprint(collection_id)
            segment = {}
            segment['collection_id'] = str(collection_id)
            segment['location'] = '/<countries>/<{}>'.format(collection_id)
            segment['indicator'] = id
            segment['creation_time'] = new_collection['creation_time']
            return segment, 201

        except Exception:
            return {"message": "the indicator = {} is not exist in the data service".format(id)}, 404

    @api.response(200, 'Successful')
    @api.doc(description='Retrieve all collections')
    def get(self):
        result = []
        for i in countries.find():
            segment = {}
            id = i['_id']
            segment['indicator'] = i['indicator']
            segment['collection_id'] = str(id)
            segment['creation_time'] = str(i['creation_time'])
            segment['location'] = "/<countries>/<{}>".format(id)
            result.append(segment)
        if not result:
            return {'message': 'there is no collection in the dataset'}
        return result, 200


@api.param('collection_id', 'The collection that the user want to search')
@api.route("/collections/<collection_id>")
class Collection(Resource):

    @api.response(400, 'Collection not found')
    @api.response(200, 'Successful')
    @api.doc(description='Delete a collection')
    def delete(self, collection_id):
        result = countries.find_one({'_id': ObjectId(collection_id)})
        if not result:
            api.abort(400, {"message": "collection = {} not in the database".format(collection_id)})
        else:
            countries.delete_one({'_id': ObjectId(collection_id)})
            return {"message": "collection = {} is removed from the database!".format(collection_id)}, 200

    @api.response(400, 'Collection not found')
    @api.response(200, 'Successful')
    @api.doc(description='Retrieve a collection')
    def get(self, collection_id):
        response = countries.find_one({"_id": ObjectId(str(collection_id))})
        if not response:
            api.abort(404, 'There is no collection ={} in the database'.format(collection_id))
        response['_id'] = str(response['_id'])
        return response, 200


@api.route('/collections/<collection_id>/<int:year>/<country>')
@api.param('collection_id', 'The collection that the user want to search')
@api.param('year', 'The year that the user want to search')
@api.param('country', 'The country that the user want to search')
class SpecificCollection(Resource):

    @api.response(400, 'Collection not found')
    @api.response(200, 'Successful')
    @api.doc(description='Retrieve a specific collection')
    def get(self, collection_id, year, country):
        try:
            result = {}
            collection = countries.find_one({'_id': ObjectId(collection_id)})
            for i in collection['entries']:
                if i['county'] == country and i['date'] == str(year):
                    result['country'] = country
                    result['date'] = str(year)
                    break
            result['indicator'] = collection['indicator']
            result['collection_id'] = collection_id
            result['value'] = collection['indicator_value']
            return result, 200
        except Exception:
            api.abort(400, 'there is no such collection in the database')


@api.route('/collections/<collection_id>/<int:year>')
@api.param('collection_id', 'The collection that the user want to search')
@api.param('year', 'The year that the user want to search')
@api.param('q', 'An optional parameter')
class GetListsCollections(Resource):

    @api.expect(parser)
    @api.doc(description='Get a list of sorted collections')
    def get(self, collection_id, year):
        collection = countries.find_one({'_id': ObjectId(collection_id)})
        if not collection:
            api.abort(404, {'message': "The collection = {} is not in the dataset".format(collection_id)})
        args = parser.parse_args()
        ascending = args.get('q')
        entries = []
        for i in collection['entries']:
            if i['date'] == str(year):
                entries.append(i)
        if ascending:
            pattern = re.compile(r'\d+')
            N = pattern.search(ascending)
            number = int(N.group(0))
            entries = sorted(entries, key= lambda x: x.__getitem__('value'), reverse=True)
            if 'top' in ascending:
                entries = entries[:number]
            elif 'bottom' in ascending:
                entries = entries[-number:]
        result = {}
        result['entries'] = entries
        result['indicator'] = collection['indicator']
        result['indicator_value'] = collection['indicator_value']
        return result, 200


if __name__ == '__main__':
    app.run(debug=True)