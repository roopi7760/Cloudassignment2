import couchdb
import json

USERNAME = "7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix"
PASSWORD = "4828714fecff497426fe357632f22a10f6d0a82e2d0f3888ea59bbad2a57e5fb"
couch = couchdb.Server("https://7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix:4828714fecff497426fe357632f22a10f6d0a82e2d0f3888ea59bbad2a57e5fb@7d79e7d0-6d67-4a21-aac0-15fff940c492-bluemix.cloudant.com")
#couch.resource.credentials(USERNAME,PASSWORD)

db = couch['appsync']

for doc in db:
    getdocs = db.get(doc)
    print getdocs['_id']
