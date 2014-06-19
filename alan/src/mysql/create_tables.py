tables={
    'EVENTS':[('GLOBALEVENTID','int primary key'), 
              ('SQLDATE','int'),
              ('Actor1Code', 'varchar'), 
              ('Actor2Code', 'varchar'),
              ('IsRootEvent', 'bool'), 
              ('EventCode', 'varchar(4)'), 
              ('GoldsteinScale', 'float'), 
              ('NumMentions', 'smallint'), 
              ('AvgTone', 'float')],

    'ACTORS':[('ActorCode','varchar(15) primary key'),
              ('ActorName','varchar(15)'),
              ('ActorCountryCode','varchar(3)'),
              ('ActorKnownGroupCode', 'varchar(9)'),
              ('ActorEthnicCode', 'varchar(9)')],
    'ACTOR_RELIGIONS':[('ActorCode','varchar(15) primary key'),
                       ('ActorReligionCode','varchar(9)')
                       ],
    'ACTOR_TYPES':[('ActorCode','varchar(15) primary key'),
                   ('ActorTypeCode','varchar(9)')],
    'EVENT_ACTOR_GEO':[('GLOBALEVENTID','int'), #unique key pair with actor num
                     ('ActorNum', 'tinyint'), #unique key pair 
                     ('Geo_Type', 'int'),
                     ('Geo_CountryCode', 'int(2)'),
                     ('Geo_ADM1Code', 'int(2)'),
                     ('Geo_Lat', 'float'),
                     ('Geo_Long', 'float'),
                     ('Geo_FeatureID', 'int')]
                     }
    

for tabname, cols in tables.items():
    cmd ='CREATE TABLE %s (' %tabname
    cmd += ','.join([' '.join(a) for a in cols])
    cmd += ');'

    print cmd
