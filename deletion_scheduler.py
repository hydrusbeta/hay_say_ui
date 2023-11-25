from datetime import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

import hay_say_common as hsc

executors = {
    'default': ThreadPoolExecutor(1)
}

scheduler = BackgroundScheduler(executors=executors)
scheduler.start()


def register_cache_cleanup_callback(cache_type):
    cache = hsc.select_cache_implementation(cache_type)

    @scheduler.scheduled_job(trigger='interval', seconds=3600, next_run_time=datetime.now())
    def print_hi():
        cutoff_in_seconds = 24*3600  # i.e. 24 hours
        print('Purging sessions older than ' + str(cutoff_in_seconds/3600) + ' hours...', flush=True)
        cache.delete_old_session_data(cutoff_in_seconds)
        print('Old sessions have been purged', flush=True)
