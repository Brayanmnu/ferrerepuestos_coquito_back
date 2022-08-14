from configparser import ConfigParser

file = "config.ini"
config = ConfigParser()
config.read(file)

def get_values_database_postgress():
    host = config['database']['host_heroku']
    port = config['database']['port_heroku']
    db = config['database']['db_heroku']
    usr = config['database']['usr_heroku']
    pwd = config['database']['pwd_heroku']
    return host, port, db, usr, pwd


def get_values_database_nosql_collection_qr():
    uri = config['mongodb']['uri'] 
    database = config['mongodb']['database'] 
    collection_qr = config['mongodb']['collection_qr'] 
    return uri, database, collection_qr

def get_values_hosting():
    return config['hosting']['url_hosting'] 
