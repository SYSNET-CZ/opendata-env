import datetime
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
EXPORT_THIS_YEAR = 0
EXPORT_PREVIOUS_YEAR = 0


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


LOG.logger.info('CHRONOS scheduled each {} hours.'.format(CHRONOS_INTERVAL_HOURS))

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
            out = import_all()
            IMPORT_ALL += 1
            LOG.logger.info('IMPORT_ALL executed ({})'.format(IMPORT_ALL))
            return out
        LOG.logger.info('Taskname {} scheduled to {}.'.format(task_name, cron))
    elif task_def[0] == 'export':
        if task_def[1] == 'all':
            @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
            def export_data():
                global EXPORT_ALL
                out = export_all()
                EXPORT_ALL += 1
                LOG.logger.info('EXPORT_ALL executed ({})'.format(EXPORT_ALL))
                return out
            LOG.logger.info('Taskname {} scheduled to {}.'.format(task_name, cron))
        elif task_def[1].isnumeric():
            year = int(task_def[1])
            this_year = datetime.datetime.now().year
            previous_year = this_year-1
            if year == this_year:
                @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
                def export_this_year():
                    global EXPORT_THIS_YEAR
                    EXPORT_THIS_YEAR += 1
                    out = export_all_for_year(year=str(year))
                    LOG.logger.info('EXPORT_THIS_YEAR[{}] executed ({})'.format(year, EXPORT_THIS_YEAR))
                    return out
                LOG.logger.info('Taskname {} scheduled to {}.'.format(task_name, cron))
            elif year == previous_year:
                @scheduler.task(trigger=trigger, id=task_name, name='openadata_' + task_name, misfire_grace_time=900)
                def export_prev_year():
                    global EXPORT_PREVIOUS_YEAR
                    EXPORT_PREVIOUS_YEAR += 1
                    out = export_all_for_year(year=str(year))
                    LOG.logger.info('EXPORT_PREVIOUS_YEAR[{}] executed ({})'.format(year, EXPORT_PREVIOUS_YEAR))
                    return out
                LOG.logger.info('Taskname {} scheduled to {}.'.format(task_name, cron))
            else:
                LOG.logger.warning('Taskname {} cannot be run.'.format(task_name))
                continue
scheduler.start()
LOG.logger.info('Scheduler started.')

if __name__ == '__main__':
    app.run(port=8080, debug=DEBUG)
