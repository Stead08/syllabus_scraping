import psycopg2
import settings

setting = settings.DATABASES['default']

connection = psycopg2.connect(
    host=setting['HOST'],
    user=setting['USER'],
    password=setting['PASSWORD'],
    database=setting['DATABASE']

)