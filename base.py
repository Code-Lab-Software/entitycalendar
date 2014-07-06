from django.db import models
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

    def sync_calendar_days(self, date_from, date_to):
        for calendar_day in models.get_model('dbcalendar', 'CalendarDay').objects.filter(date__range=[date_from, date_to]):
            self.sync_calendar_day(calendar_day)

    def sync_calendar_day(self, calendar_day):
        for entity in self.model.entity_model.objects.all():
            entity_attr_name = self.model.entity_attr_name
            calendar_year_model = models.get_model(self.model.entity_app_name, '%sCalendarYear' % self.model.entity_attr_name.title())
            calendar_month_model = models.get_model(self.model.entity_app_name, '%sCalendarMonth' % self.model.entity_attr_name.title())
            calendar_week_model = models.get_model(self.model.entity_app_name, '%sCalendarWeek' % self.model.entity_attr_name.title())
            calendar_day_model = models.get_model(self.model.entity_app_name, '%sCalendarDay' % self.model.entity_attr_name.title())
            
            entity_year, created = calendar_year_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_year': calendar_day.calendar_month.calendar_year})
            entity_month, created = calendar_month_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_month': calendar_day.calendar_month,
                                                                                  '%s_year' % entity_attr_name: entity_year})
            entity_week, created = calendar_week_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_week': calendar_day.calendar_week,
                                                                                  '%s_year' % entity_attr_name: entity_year})

            entity_day, created = calendar_day_model.objects.get_or_create(**{entity_attr_name: entity, 'calendar_day': calendar_day,
                                                                              '%s_week' % entity_attr_name: entity_week, '%s_month' % entity_attr_name: entity_month})


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

    def __unicode__(self):
        return u"%s - %s" % (self.get_entity(), self.calendar_day)


    class Meta:
        abstract = True


