from twisted.enterprise import adbapi

db_pool_lookup = {}
def getConnection(zid):
    global db_pool_lookup
    return db_pool_lookup[zid]


def initialize(access_list):
    global db_pool_lookup
    for (zid, dbtype, dbname, user, password, host, port) in access_list:
        dbpool = adbapi.ConnectionPool("MySQLdb", db="test", user=user, password=password)
        db_pool_lookup[zid] = dbpool
