from __future__ import unicode_literals
import math
from django.db.models import Q
from evennia.utils.utils import time_format
from evennia.locks.lockhandler import LockException
from athanor.jobs.models import JobCategory, Job, JobHandler, JobComment
from athanor.core.command import AthCommand
from athanor.utils.text import normal_string
from athanor.utils.time import utcnow, duration_from_string

class CmdJob(AthCommand):
    key = '+job'
    aliases = ['+jobs']
    system_name = 'JOBS'
    player_switches = ['reply', 'old', 'approve', 'deny', 'cancel', 'revive', 'comment', 'due', 'claim', 'unclaim',
                       'attn', 'scan', 'next', 'pending', 'addhelper', 'remhelper', 'brief', 'search']
    admin_switches = ['newcategory', 'delcategory', 'rencategory', 'lock', 'move', 'config']
    page = 1
    jobs = None

    def func(self):
        pages = [int(swi) for swi in self.switches if swi.isdigit()]
        if pages:
            self.page = pages[0]

        rhs = self.rhs
        lhs = self.lhs
        switches = [swi for swi in self.final_switches if not isinstance(swi, int)]

        if switches:
            switch = switches[0]
            try:
                return getattr(self, 'switch_%s' % switch)(lhs, rhs)
            except ValueError as err:
                return self.error(str(err))
        if self.args:
            return self.switch_display(lhs, rhs)
        else:
            self.list_categories(lhs, rhs)

    def list_categories(self, lhs, rhs):
        message = list()
        message.append(self.player.render.header('Job Categories'))
        cat_table = self.player.render.make_table(['Name', 'Description', 'Pen', 'App', 'Dny', 'Cnc', 'Over', 'Due', 'Anon'],
                                                    width=[10, 35, 5, 5, 5, 5, 5, 5, 5])
        for cat in JobCategory.objects.all().order_by('key'):
            pending = cat.jobs.filter(status=0).count()
            approved = cat.jobs.filter(status=1).count()
            denied = cat.jobs.filter(status=2).count()
            canceled = cat.jobs.filter(status=3).count()
            anon = 'Yes' if cat.anonymous else 'No'
            now = utcnow()
            overdue = cat.jobs.filter(status=0, due_date__lt=now).count()
            due = time_format(cat.due.total_seconds(), style=1)
            cat_table.add_row(cat.key, cat.description, pending, approved, denied, canceled, overdue, due, anon)
        message.append(cat_table)
        message.append(self.player.render.footer())
        self.msg_lines(message)


    def switch_newcategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            return self.error("Permission denied!")
        name = normal_string(lhs)
        if not name:
            return self.error("Nothing entered to create.")
        if name.isdigit():
            raise ValueError("Can't name Job categories numbers!")
        found = JobCategory.objects.filter(key__iexact=name).count()
        if found:
            return self.error("Category already exists. Use /rencategory to rename it.")
        due = self.valid_duration('1w')
        cat, created = JobCategory.objects.get_or_create(key=name, due=due)
        msg = "Created New Job Category: %s" % name
        self.sys_report(msg)
        self.sys_msg(msg)

    def valid_jobcategory(self, entry=None, check_permission=''):
        if not entry:
            raise ValueError("Job category name field empty.")
        choices = JobCategory.objects.all().order_by('key')
        if check_permission:
            choices = [cat for cat in choices if cat.locks.check(self.character, check_permission)]
        found = self.partial(entry, choices)
        if not found:
            raise ValueError("Job Category not found or permission denied.")
        return found

    def switch_rencategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            self.error("Permission denied!")
            return
        try:
            cat = self.valid_jobcategory(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        name = normal_string(rhs)
        if name.isdigit():
            raise ValueError("Can't name Job categories numbers!")
        if not name:
            return self.error("Job category new name field empty.")
        found = JobCategory.objects.exclude(id=cat.id).filter(key__iexact=name).first()
        if found:
            return self.error("That would conflict with an existing category.")
        msg = "Renamed Job Category '%s' to '%s'!" % (cat.key, name)
        cat.key = name
        cat.save(update_fields=['key'])
        self.sys_msg(msg)
        self.sys_report(msg)

    def switch_delcategory(self, lhs, rhs):
        if not self.player.account.is_immortal():
            self.error("Permission denied!")
            return
        try:
            cat = self.valid_jobcategory(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        if not self.verify('delete job category %s' % cat.id):
            self.sys_msg("This will delete the Job Category '%s' and ALL ASSOCIATED JOBS. This cannot be undone."
                         "Enter the same command again in ten seconds to verify!")

    def switch_lock(self, lhs, rhs):
        if not self.player.account.is_immortal():
            self.error("Permission denied!")
            return
        try:
            cat = self.valid_jobcategory(lhs)
        except ValueError as err:
            self.error(str(err))
            return
        if not rhs:
            self.error("Must enter a lockstring.")
            return
        for locksetting in rhs.split(';'):
            access_type, lockfunc = locksetting.split(':', 1)
            if not access_type:
                self.error("Must enter an access type: post or admin.")
                return
            accmatch = self.partial(access_type, ['admin', 'post'])
            if not accmatch:
                self.error("Access type must be post or admin.")
                return
            if not lockfunc:
                self.error("Lock func not entered.")
                return
            ok = False
            try:
                ok = cat.locks.add(rhs)
                cat.save_locks()
            except LockException as e:
                self.error(unicode(e))
            if ok:
                msg = "Added lock '%s' to %s." % (rhs, cat)
                self.sys_msg(msg)
                self.sys_report(msg)
            return


    def valid_job(self, entry=None, check_access=True):
        if not entry:
            raise ValueError("Must enter a Job ID.")
        job_id = self.valid_posint(entry)
        found = Job.objects.filter(id=job_id).first()
        if not found:
            raise ValueError("Job %s not found." % job_id)
        handler, created = found.characters.get_or_create(character=self.character)
        if not check_access:
            return found
        if found.locks.check(self.character, 'admin'):
            return found
        if handler.is_handler or handler.is_owner or handler.is_helper:
            return found
        raise ValueError("Permission denied.")


    def switch_move(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied. Need admin on source category.")
        self.check_finished(job)
        cat = self.valid_jobcategory(rhs, check_permission='admin')
        job.change_category(self.character, cat)


    def switch_config(self, lhs, rhs):
        pass


    def switch_display(self, lhs, rhs, old=False):
        if not lhs:
            raise ValueError("What will you display?")
        if lhs.isdigit():
            return self.display_job(lhs)
        return self.display_category(lhs, old)

    def switch_old(self, lhs, rhs):
        return self.switch_display(lhs, rhs, old=True)

    def display_category(self, lhs, old=False):
        cat = self.valid_jobcategory(lhs)
        viewer = self.character
        page = self.page
        message = list()
        if old:
            jobs = cat.jobs.exclude(status=0).order_by('id').reverse()
        else:
            interval = utcnow() - duration_from_string('7d')
            jobs = cat.jobs.filter(Q(status=0, close_date=None) | Q(close_date__gte=interval)).order_by('id').reverse()
        jobs_count = jobs.count()
        pages = float(jobs_count) / 30.0
        pages = int(math.ceil(pages))
        if page > pages:
            page = pages
        if not pages:
            raise ValueError("No jobs to display!")
        start = (page - 1) * 30
        show = list(jobs[start:start+30])
        show.reverse()
        message.append(viewer.render.header('Jobs - %s' % cat))
        job_table = viewer.render.make_table(["*", "ID", "From", "Title", "Due", "Handling", "Upd", "LstAct"],
                                             width=[3, 4, 25, 18, 5, 10, 5, 10])
        for j in show:
            sta = j.status_letter()
            due = ''
            handle = ', '.join([hand.character.key for hand in j.handlers()])
            upd = ''
            job_table.add_row(sta, j.id, j.owner, j.title, due, handle, upd, j.last_from)
        message.append(job_table)
        foot = '< Page %s of %s >' % (page, pages)
        message.append(viewer.render.footer(foot))
        self.msg_lines(message)

    def display_job(self, lhs):
        job = self.valid_job(lhs, check_access=True)
        handler, created = job.characters.get_or_create(character=self.character)
        handler.check()
        self.msg_lines(job.display(self.character))

    def switch_claim(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied. Need admin on source category.")
        if not rhs:
            return job.appoint_handler(self.character, self.character)
        self.check_finished(job)
        for target in self.rhslist:
            find = None
            try:
                find = self.character.search_character(target)
                job.appoint_handler(self.character, find)
            except ValueError as err:
                self.error(str(err))

    def switch_unclaim(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied. Need admin on source category.")
        self.check_finished(job)
        if not rhs:
            return job.remove_handler(self.character, self.character)
        for target in self.rhslist:
            find = None
            try:
                find = self.character.search_character(target)
                job.remove_handler(self.character, find)
            except ValueError as err:
                self.error(str(err))

    def switch_addhelper(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied. Need admin on source category.")
        self.check_finished(job)
        if not rhs:
            return job.appoint_helper(self.character, self.character)
        for target in self.rhslist:
            find = None
            try:
                find = self.character.search_character(target)
                job.appoint_helper(self.character, find)
            except ValueError as err:
                self.error(str(err))

    def switch_remhelper(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied. Need admin on source category.")
        self.check_finished(job)
        if not rhs:
            return job.remove_helper(self.character, self.character)
        for target in self.rhslist:
            find = None
            try:
                find = self.character.search_character(target)
                job.remove_helper(self.character, find)
            except ValueError as err:
                self.error(str(err))

    def check_finished(self, job):
        if not job.status == 0:
            raise ValueError("Cannot modify Job %s. It is %s." % (job.id, job.status_word()))

    def switch_reply(self, lhs, rhs):
        job = self.valid_job(lhs)
        self.check_finished(job)
        if not rhs:
            return self.error("What will you say?")
        job.make_reply(self.character, rhs)

    def switch_comment(self, lhs, rhs):
        job = self.valid_job(lhs)
        handler, created = job.characters.get_or_create(character=self.character)
        if not job.locks.check(self.character, 'admin') or handler.is_handler:
            raise ValueError("Permission denied.")
        self.check_finished(job)
        if not rhs:
            return self.error("What will you say?")
        job.make_comment(self.character, rhs)

    def switch_approve(self, lhs, rhs):
        job = self.valid_job(lhs)
        handler, created = job.characters.get_or_create(character=self.character)
        if not job.locks.check(self.character, 'admin') or handler.is_handler:
            raise ValueError("Permission denied.")
        if not rhs:
            return self.error("What will you say?")
        job.set_approved(self.character, rhs)

    def switch_deny(self, lhs, rhs):
        job = self.valid_job(lhs)
        handler, created = job.characters.get_or_create(character=self.character)
        if not job.locks.check(self.character, 'admin') or handler.is_handler:
            raise ValueError("Permission denied.")
        if not rhs:
            return self.error("What will you say?")
        job.set_denied(self.character, rhs)

    def switch_cancel(self, lhs, rhs):
        job = self.valid_job(lhs)
        handler, created = job.characters.get_or_create(character=self.character)
        if not job.locks.check(self.character, 'admin') or handler.is_handler:
            raise ValueError("Permission denied.")
        if not rhs:
            return self.error("What will you say?")
        job.set_canceled(self.character, rhs)

    def switch_revive(self, lhs, rhs):
        job = self.valid_job(lhs)
        handler, created = job.characters.get_or_create(character=self.character)
        if not job.locks.check(self.character, 'admin') or handler.is_handler:
            raise ValueError("Permission denied.")
        if not rhs:
            return self.error("What will you say?")
        job.set_pending(self.character, rhs)

    def switch_due(self, lhs, rhs):
        job = self.valid_job(lhs)
        if not job.locks.check(self.character, 'admin'):
            raise ValueError("Permission denied.")
        new_date = self.valid_date(rhs, self.player)
        job.set_due(self.character, new_date)


class CmdRequest(AthCommand):
    key = '+request'
    system_name = 'REQUEST'

    def func(self):
        default = self.settings.get('job_default')
        if default.value:
            category = default.value
        else:
            category = None
        if not self.switches and not category:
            return self.error("No default set. Must use a /switch to choose Category.")
        if self.switches:
            choices = [cat for cat in JobCategory.objects.all().order_by('key')
                       if cat.locks.check(self.character, 'post')]
            switch = self.switches[0]
            found = self.partial(switch, choices)
            if not found:
                return self.error("Category '%s' not Found. Choices are: %s" % (switch, ', '.join(cat.key for cat in choices)))
            category = found
        if not category:
            return self.error("Category not found!")
        if not category.locks.check(self.character, 'post'):
            return self.error("Permission denied!")
        title = normal_string(self.lhs)
        if not title:
            return self.error("Must enter a subject!")
        opening = self.rhs
        if not opening:
            self.error("No opening text included!")
        category.make_job(self.character, title, opening)


"""
player_switches = ['reply', 'old', 'approve', 'deny', 'cancel', 'revive', 'comment', 'due', 'claim', 'unclaim',
                   'attn', 'scan', 'next', 'pending', 'addplayer', 'remplayer', 'brief', 'search']
"""

class CmdMyJob(CmdJob):
    key = '+myjob'
    aliases = ['+myjobs']
    system_name = 'MYJOBS'
    player_switches = ['reply', 'old', 'approve', 'deny', 'cancel', 'revive', 'comment', 'due', 'claim', 'unclaim',
                       'addhelper', 'remhelper']
    admin_switches = []

    def switch_display(self, lhs, rhs, old=False):
        if not lhs:
            return self.list_categories(lhs, rhs, old)
        if lhs.isdigit():
            return self.display_job(lhs)
        raise ValueError("What will you display?")

    def switch_old(self, lhs, rhs):
        return self.switch_display(lhs, rhs, old=True)

    def list_categories(self, lhs, rhs, old=False):
        viewer = self.character
        page = self.page
        message = list()
        jobs = Job.objects.filter(characters__character=self.character).order_by('id').reverse()
        jobs = jobs.filter(Q(characters__is_handler=True) | Q(characters__is_helper=True) | Q(characters__is_owner=True))
        if old:
            jobs = jobs.exclude(status=0)
        else:
            interval = utcnow() - duration_from_string('7d')
            jobs = jobs.filter(Q(status=0, close_date=None) | Q(close_date__gte=interval))
        jobs_count = jobs.count()
        pages = float(jobs_count) / 30.0
        pages = int(math.ceil(pages))
        if page > pages:
            page = pages
        if not pages:
            raise ValueError("No jobs to display!")
        start = (page - 1) * 30
        show = list(jobs[start:start + 30])
        show.reverse()
        message.append(viewer.render.header('MyJobs'))
        job_table = viewer.render.make_table(["*", "ID", "Cat", "From", "Title", "Due", "Handling", "Upd", "LstAct"],
                                             width=[3, 4, 8, 21, 16, 5, 10, 5, 8])
        for j in show:
            sta = j.status_letter()
            cat = j.category.key
            due = ''
            handle = ', '.join([hand.character.key for hand in j.handlers()])
            upd = ''
            job_table.add_row(sta, j.id, cat, j.owner, j.title, due, handle, upd, j.last_from)
        message.append(job_table)
        foot = '< Page %s of %s >' % (page, pages)
        message.append(viewer.render.footer(foot))
        self.msg_lines(message)