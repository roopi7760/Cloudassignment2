import couchdb
import json

couch = couchdb.Server("")
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


for docs in db:
    doc = db.get(docs)
    if (doc['version']) :
        print doc['version']
'''for d in doc['version']:
    d = d.encode('ascii','ignore')
    print doc['version'][d]['rev_content']
#doc['version'][mversion] = None # {'rev_content': None, 'rev_hashcode':None, 'datemodified': None}
#db.save(doc)
#print doc'''