'''
Population functions for the CMS.
'''

import re, cPickle, random, datetime
from gluon.contrib.populate import Learner, IUP, da_du_ma

def populate(table, n, default=True, values=None):
    """
    Custom population function, for web2cms
    
    :param table: Table to populate
    :param n: Amount of records to generate
    :param default: Whether to use default value if one specified, or not
    :param values: A list to be used to populate fields. It can be:
        - a fixed value, used directly
        - callable: will be called with (table, fieldname) and the
          return value used as field value
    """
    ell=Learner()
    #ell.learn(open('20417.txt','r').read())
    #ell.save('frequencies.pickle')
    #ell.load('frequencies.pickle')
    ell.loadd(IUP)
    ids={}
    for i in range(n):
        record={}
        for fieldname in table.fields:
            field = table[fieldname]
            if not isinstance(field.type,(str,unicode)):
                continue
            elif field.type == 'id':
                continue
            
            ## --- [SAMU 2011-11-01] BEGIN
            elif values is not None and values.has_key(fieldname):
                if callable(values[fieldname]):
                    record[fieldname] = values[fieldname](table, fieldname)
                else:
                    record[fieldname]=values[fieldname]
            ## --- END
            
            elif default and field.default:
                record[fieldname]=field.default
            elif field.type == 'text':
                record[fieldname]=ell.generate(random.randint(10,100),prefix=None)
            elif field.type == 'boolean':
                record[fieldname]=random.random()>0.5
            elif field.type == 'date':
                record[fieldname] = \
                    datetime.date(2009,1,1) - \
                    datetime.timedelta(days=random.randint(0,365))
            elif field.type == 'datetime':
                record[fieldname] = \
                    datetime.datetime(2009,1,1) - \
                    datetime.timedelta(days=random.randint(0,365))
            elif field.type == 'time':
                h = random.randint(0,23)
                m = 15*random.randint(0,3)
                record[fieldname] = datetime.time(h,m,0)
            elif field.type == 'password':
                record[fieldname] = ''
            elif field.type == 'upload':
                record[fieldname] = None
            elif field.type=='integer' and hasattr(field.requires,'options'):
                options=field.requires.options(zero=False)
                if len(options)>0:
                    record[fieldname] = options[random.randint(0,len(options)-1)][0]
                else:
                    record[fieldname] = None
            elif field.type=='list:integer' and hasattr(field.requires,'options'):
                options=field.requires.options(zero=False)
                if len(options) > 0:
                    vals = []
                    for i in range(0, random.randint(0,len(options)-1)/2):
                        vals.append(options[random.randint(0,len(options)-1)][0])
                    record[fieldname] = vals
            elif field.type in ['integer','double'] or str(field.type).startswith('decimal'):
                try:
                    record[fieldname] = random.randint(field.requires.minimum,field.requires.maximum-1)
                except:
                    record[fieldname] = random.randint(0,1000)
            elif field.type[:10] == 'reference ':
                tablename = field.type[10:]
                if not tablename in ids:
                    if table._db._dbname=='gql':
                        ids[tablename] = [x.id for x in table._db(table._db[field.type[10:]].id>0).select()]
                    else:
                        ids[tablename] = [x.id for x in table._db(table._db[field.type[10:]].id>0).select()]
                n = len(ids[tablename])
                if n:
                    record[fieldname] = ids[tablename][random.randint(0,n-1)]
                else:
                    record[fieldname] = 0
            elif field.type[:15] == 'list:reference ':
                tablename = field.type[15:]
                if not tablename in ids:
                    if table._db._dbname=='gql':
                        ids[tablename] = [x.id for x in table._db(table._db[field.type[15:]].id>0).select()]
                    else:
                        ids[tablename] = [x.id for x in table._db(table._db[field.type[15:]].id>0).select()]
                n = len(ids[tablename])
                if n:
                    vals = []
                    for i in range(0, random.randint(0,n-1)/2):
                        vals.append(ids[tablename][random.randint(0,n-1)])
                    record[fieldname] = vals
                else:
                    record[fieldname] = 0
            elif field.type=='list:string' and hasattr(field.requires,'options'):
                options=field.requires.options(zero=False)
                if len(options) > 0:
                    vals = []
                    for i in range(0, random.randint(0,len(options)-1)/2):
                        vals.append(options[random.randint(0,len(options)-1)][0])
                    record[fieldname] = vals
            elif field.type=='string' and hasattr(field.requires,'options'):
                options=field.requires.options(zero=False)
                record[fieldname] = options[random.randint(0,len(options)-1)][0]
            elif field.type=='string' and fieldname.find('url')>=0:
                record[fieldname] = 'http://%s.example.com' % da_du_ma(4)
            elif field.type=='string' and fieldname.find('email')>=0:
                record[fieldname] = '%s@example.com' % da_du_ma(4)
            elif field.type=='string' and fieldname.find('name')>=0:
                record[fieldname] = da_du_ma(4).capitalize()
            elif field.type=='string':
                record[fieldname] = ell.generate(10, prefix=False)[:field.length].replace('\n',' ')
        table.insert(**record)
    table._db.commit()
