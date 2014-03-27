import os
import urlparse
import redis
from redis import Redis
from rq import Worker, Queue, Connection, use_connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'localhost')  # 'redis://localhost:6379')

"""
if not redis_url:
    raise RuntimeError('Set up Redis To Go first.')
"""
urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
# conn.set('answer', 42)
# conn.get('answer')


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
