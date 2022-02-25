#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         scheduler
# Purpose:      Schedules import and export tasks
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2022
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from exporter import export_all_data
from importer import import_jasu_all
from settings import LOG, CONFIG, create_map_from_list


def export_all():
    return export_all_data()


def export_all_for_year(year=None):
    return export_all_data(year=year)


def import_all():
    return import_jasu_all()


def cron_to_dict(cron):
    if cron is None:
        return None
    cron_list = cron.split(' ')
    if len(cron_list) != 5:
        return None
    out = {
        'minute': cron_list[0],
        'hour': cron_list[1],
        'day': cron_list[2],
        'month': cron_list[3],
        'day_of_week': cron_list[4]
    }
    return out


SCHEDULER = BlockingScheduler(timezone="Europe/Prague")


def init_tasks():
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
            SCHEDULER.add_job(
                func=import_all,
                id=task_name,
                name='openadata_' + task_name,
                trigger=trigger,
                max_instances=1,
                replace_existing=True
            )
            LOG.logger.info('Added task {}: {}'.format(task_name, cron))
        elif task_def[0] == 'export':
            if task_def[1] == 'all':
                SCHEDULER.add_job(
                    func=export_all,
                    id=task_name,
                    name='openadata_' + task_name,
                    trigger=trigger,
                    max_instances=1,
                    replace_existing=True
                )
                LOG.logger.info('Added task {}: {}'.format(task_name, cron))
            elif task_def[1].isnumeric():
                kwargs = {
                    'year': task_def[1],
                }
                SCHEDULER.add_job(
                    func=export_all_for_year,
                    kwargs=kwargs,
                    id=task_name,
                    name='openadata_' + task_name,
                    trigger=trigger,
                    max_instances=1,
                    replace_existing=True
                )
                LOG.logger.info('Added task {}: {}'.format(task_name, cron))


def main():
    init_tasks()
    SCHEDULER.start()
    SCHEDULER.print_jobs()


if __name__ == "__main__":
    main()
