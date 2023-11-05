import configparser

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from guard import Guard

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    inverterGuard = Guard(config)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(inverterGuard.login, 'interval', seconds=60, max_instances=1)
    scheduler.add_job(inverterGuard.run_guard, 'interval', seconds=20, max_instances=1)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()

