# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver


from pubtracker.models import PublicationTracker

class EntityCalendarBase(PublicationTracker):
    
    def get_entity(self):
        return getattr(self, 'entity_attr_name')
        
    class Meta:
        abstract = True

class EntityCalendarYear(EntityCalendarBase):
    # ENTITY_ATTR_NAME = models.ForeignKey(ENTITY_MODEL, verbose_name=ENTITY_VERBOSE_NAME, related_name="{ENTITY_ATTR_NAME}calendaryears")
    # calendar_year = models.ForeignKey('dbcalendar.CalendarYear', verbose_name=u"Calendar year", related_name="{ENTITY_ATTR_NAME}calendaryears")
    #
    # class Meta:
    #    unique_together = (('ENTITY_ATTR_NAME', 'calendar_year'),)
    #    verbose_name = u"{ENTITY_ATTR_NAME} calendar year"
    #    verbose_name_plural = u"{ENTITY_ATTR_NAME} calendar years"

    def __unicode__(self):
        return u"%s - %s" % (self.get_entity(), self.calendar_year)

    class Meta:
        abstract = True


class EntityCalendarMonth(EntityCalendarBase):
    # ENTITY_ATTR_NAME = models.ForeignKey(ENTITY_MODEL, verbose_name=ENTITY_VERBOSE_NAME, related_name="{ENTITY_ATTR_NMAE}calendarmonths")
    # {ENTITY_ATTR_NAME}_year = models.ForeignKey('{ENTITY}CalendarYear', verbose_name=u"{ENTITY_ATTR_NAME} calendar year", related_name="{ENTITY_ATTR_NAME}calendarmonths")
    # calendar_month = models.ForeignKey('dbcalendar.CalendarMonth', verbose_name=u"Calendar month", related_name="{ENTITY}calendarmonths")
    #
    # class Meta:
    #     unique_together = (('calendar_month', '{ENTITY_ATTR_NAME}_year'),)
    #     verbose_name = u"{ENTITY_ATTR_NAME} calendar month"
    #     verbose_name_plural = u"{ENTITY_ATTR_NAME} calendar month"

    class Meta:
        abstract = True


class EntityCalendarWeek(EntityCalendarBase):
    # room = models.ForeignKey('dormitorysetup.Room', verbose_name="Room", related_name="roomcalendarweeks")
    # room_year = models.ForeignKey('RoomCalendarYear', verbose_name=u"Room calendar year", related_name="roomcalendarweeks")
    # calendar_week = models.ForeignKey('dbcalendar.CalendarWeek', verbose_name=u"Calendar week", related_name="roomcalendarweeks")

    # class Meta:
    #     unique_together = (('calendar_week', 'room_year'),)
    #     verbose_name = u"Room calendar week"
    #     verbose_name_plural = u"Room calendar week"

    class Meta:
        abstract = True


class EntityCalendaryDayManager(models.Manager):

    def sync_calendar_days(self, entity=None, date_from=None, date_to=None):
        dates = models.get_model('dbcalendar', 'CalendarDay').objects.all()
        if date_from:
            dates = dates.filter(date__gte=date_from)
        if date_to:
            dates = dates.filter(date_lte=date_tom)
        total_count = dates.count()
        i = 0
        print 'Sync. days %d, dla %s' % (total_count, entity)
        for calendar_day in dates:
            self.sync_calendar_day(calendar_day, entity)
            i += 1

    def sync_calendar_day(self, calendar_day, entity=None):
        entity_attr_name = self.model.entity_attr_name
        calendar_year_model = models.get_model(self.model.entity_app_name, '%sCalendarYear' % self.model.entity_attr_name.title())
        calendar_month_model = models.get_model(self.model.entity_app_name, '%sCalendarMonth' % self.model.entity_attr_name.title())
        calendar_week_model = models.get_model(self.model.entity_app_name, '%sCalendarWeek' % self.model.entity_attr_name.title())
        calendar_day_model = models.get_model(self.model.entity_app_name, '%sCalendarDay' % self.model.entity_attr_name.title())

        for entity in self.model.entity_model.objects.all().iterator() if entity is None else [entity]:
            self.sync_entity_calendar_day(entity, calendar_day, entity_attr_name, calendar_year_model, calendar_month_model, calendar_week_model, calendar_day_model)


    def sync_entity_calendar_day(self, entity, calendar_day, entity_attr_name, calendar_year_model, calendar_month_model, calendar_week_model, calendar_day_model):
        entity_year, created = calendar_year_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_year': calendar_day.calendar_month.calendar_year})
        entity_month, created = calendar_month_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_month': calendar_day.calendar_month, '%s_year' % entity_attr_name: entity_year})
        entity_week, created = calendar_week_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_week': calendar_day.calendar_week, '%s_year' % entity_attr_name: entity_year})
        entity_day, created = calendar_day_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_day': calendar_day,'%s_week' % entity_attr_name: entity_week, '%s_month' % entity_attr_name: entity_month})
        


# -------------------------------------------------------
# Trakery modeli tworzonych dynamicznie
# -------------------------------------------------------
class EntityCalendarDayTracker(ModelBase):
    def __new__(cls, name, bases, attrs):
        _new = super(EntityCalendarDayTracker, cls).__new__(cls, name, bases, attrs)
        if name != 'EntityCalendarDay':
            _new.register_model(_new)
        return _new

def sync_entity_calendar_day_post_save(sender, instance, created, raw, using, **kwargs):
    getattr(instance, '%scalendardays' % instance._meta.object_name.lower()).model.objects.sync_calendar_days(instance)

class EntityCalendarDay(EntityCalendarBase):
    # room = models.ForeignKey('dormitorysetup.Room', verbose_name=u"Room", related_name="roomcalendardays", on_delete=models.PROTECT)
    # room_week = models.ForeignKey('RoomCalendarWeek', verbose_name=u"Room week", related_name="roomcalendardays", on_delete=models.PROTECT)
    # room_month = models.ForeignKey('RoomCalendarMonth', verbose_name=u"Room month", related_name="roomcalendardays", on_delete=models.PROTECT)
    # calendar_day = models.ForeignKey('dbcalendar.CalendarDay', verbose_name=u"Calendar day", related_name="roomcalendardays", on_delete=models.PROTECT)

    # class Meta:
    #     unique_together = ( ('room_week', 'calendar_day'),)
    #     verbose_name = u"Room calendar day"
    #     verbose_name_plural = u"Room calendar days"

    objects = EntityCalendaryDayManager()

    _reqistry = []
    __metaclass__ = EntityCalendarDayTracker

    @classmethod
    def register_model(cls, mdl):
        # Register mdl and connect its entity_model with post-save handler
        # that will create all required EntityCalendar objects on object creation
        cls._reqistry.append(mdl)
        post_save.connect(sync_entity_calendar_day_post_save, sender=cls.entity_model, dispatch_uid="sync_entity_calendar_day_post_save_%s_%s" % (mdl._meta.app_label, mdl._meta.object_name.lower()))

    def __unicode__(self):
        return u"%s - %s" % (self.get_entity(), self.calendar_day)

    class Meta:
        abstract = True


