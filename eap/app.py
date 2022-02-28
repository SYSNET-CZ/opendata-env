import os
from logging.config import dictConfig

from apscheduler.triggers.cron import CronTrigger
from flask import Flask
from flask_apscheduler import APScheduler

from scheduler import cron_to_dict, import_all, export_all, export_all_for_year
from settings import set_ext_logger, LOG, create_map_from_list, CONFIG

SERVICE_ENVIRONMENT = os.getenv("SERVICE_ENVIRONMENT", "development")
CHRONOS_INTERVAL_HOURS = os.getenv("CHRONOS_INTERVAL_HOURS", '1')
CHRONOS = 0
IMPORT_ALL = 0
EXPORT_ALL = 0
EXPORT_YEAR = 0


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_API_PREFIX = '/scheduler'
    SCHEDULER_ENDPOINT_PREFIX = 'scheduler.'
    SCHEDULER_ALLOWED_HOSTS = ['*']
    SERVICE_ENVIRONMENT = SERVICE_ENVIRONMENT
    SCHEDULER_TIMEZONE = "Europe/Prague"


DEBUG = True
if SERVICE_ENVIRONMENT == 'production':
    DEBUG = False

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s - %(levelname)s in %(module)s - %(name)s: %(message)s',
        'datefmt': '%d.%m.%Y %H:%M:%S'
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
app.logger.info("FLASK logger configured!")
set_ext_logger(app.logger)


@scheduler.task('interval', id='chronos', hours=int(CHRONOS_INTERVAL_HOURS), misfire_grace_time=900)
def chronos():
    global CHRONOS
    CHRONOS += 1
    LOG.logger.info('CHRONOS executed ({})'.format(CHRONOS))


cm = create_map_from_list(CONFIG['scheduler'])
for task_name in cm.keys():
    task_def = task_name.split('_')
    cron = cm[task_name]
    tr = cron_to_dict(cron=cron)
    if tr is None:
        continue
    trigger = CronTrigger(
        minute=tr['minute'],
        hour=tr['hour'],
        day=tr['day'],
        month=tr['month'],
        day_of_week=tr['day_of_week']
    )
    if task_def[0] == 'import':
        if task_def[1] != 'all':
            continue

        @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
        def import_data():
            global IMPORT_ALL
            IMPORT_ALL += 1
            LOG.logger.info('IMPORT_ALL executed ({})'.format(IMPORT_ALL))
            return import_all
    elif task_def[0] == 'export':
        if task_def[1] == 'all':
            @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
            def export_data():
                global EXPORT_ALL
                EXPORT_ALL += 1
                LOG.logger.info('EXPORT_ALL executed ({})'.format(EXPORT_ALL))
                return export_all
        elif task_def[1].isnumeric():
            @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
            def export_year():
                global EXPORT_YEAR
                EXPORT_YEAR += 1
                LOG.logger.info('EXPORT_YEAR executed ({})'.format(EXPORT_YEAR))
                return export_all_for_year(year=task_def[1])

scheduler.start()

if __name__ == '__main__':
    app.run(port=8080, debug=DEBUG)
