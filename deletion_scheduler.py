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
    @scheduler.scheduled_job(trigger='interval', seconds=1)
    def print_hi():
        # todo: make this clean up the cache periodically
        print("hi there!", flush=True)
