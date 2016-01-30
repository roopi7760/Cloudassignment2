import couchdb
import json

USERNAME = "be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix"
PASSWORD = "473146b3b4d9073f3f02c83b97b5f8778a45a62e94177c1a1ecd1601edd24cfa"

couch = couchdb.Server("https://be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix:473146b3b4d9073f3f02c83b97b5f8778a45a62e94177c1a1ecd1601edd24cfa@be8dae94-2e36-4ff1-ba74-bdc4f6be1804-bluemix.cloudant.com")
#couch.resource.credentials(USERNAME,PASSWORD)
mversion = '1'
db = couch['appsync']
'''db.save({
            '_id' : 'hi3.txt',
            'version':
                {
                    1 :
                         {
                        'rev_content': 'content1',
                        'rev_hashcode' : 'filehash1',
                        'datemodified' : 'datemodified1'
                        },
                    2 :
                        {
                        'rev_content': 'content2',
                        'rev_hashcode' : 'filehash2',
                        'datemodified' : 'dateModified2'
                        }
                }
            })'''

doc = db.get('hi.txt')
for d in doc['version']:
    d = d.encode('ascii','ignore')
    print doc['version'][d]['rev_content']
#doc['version'][mversion] = None # {'rev_content': None, 'rev_hashcode':None, 'datemodified': None}
#db.save(doc)
#print doc