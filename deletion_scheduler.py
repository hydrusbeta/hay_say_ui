from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from hay_say_common import *

executors = {
    'default': ThreadPoolExecutor(1)
}

scheduler = BackgroundScheduler(executors=executors)
scheduler.start()


def register_cache_cleanup_callback(cache_type):
    cache = select_cache_implementation(cache_type)

    @scheduler.scheduled_job(trigger='interval', seconds=3600)
    def print_hi():
        cutoff_in_seconds = 24*3600  # i.e. 24 hours
        print('Purging sessions older than ' + str(cutoff_in_seconds/3600) + ' hours...', flush=True)
        cache.delete_old_session_data(cutoff_in_seconds)
        print('Old sessions have been purged', flush=True)
