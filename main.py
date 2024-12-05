import pkg.dbs.postgres
from pkg import config
from pkg import claude


def main() :
    path = config.getArg()

    conf = config.getConfig(path)
    pconf = conf['postgres']
    psql = pkg.dbs.postgres.PSQL(pconf['host'], int(pconf['port']),pconf['db'],pconf['user'],pconf['pw'])
    res = psql.get_db_schema()
    print(res)
    # key = config.get_API_keys()
    # claude.request("PostgreSQL", res, 'List the name, born state and age of the heads of departments ordered by age.', key)

if __name__ == '__main__':
    main()
