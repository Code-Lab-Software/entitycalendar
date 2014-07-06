import base

from django.db import models
from django.conf import settings

def get_model_name(model, attr_name, period_type):
    return "%sCalendar%s" % (attr_name.title(), period_type.title())

class EntityCalendarFactory(object):
    """ This is a factory class - it will dynamically create
        entity-calendar-type models using the information stored in 
        the registry classes list in `registry.classes`.

    """

    def register_entity_calendar(self, attr_name, model, app_name='dbcalendar', mixins=None):
        for period_type in ('year', 'month', 'week', 'day'):
            self.create_entity_calendar_model(period_type, attr_name, model, app_name, mixins.get(period_type)) 

    def create_entity_calendar_model(self, period_type, attr_name, model, app_name, mixins):
        attrs = {'__module__': "%s.models" % app_name, 'entity_attr_name': attr_name, 
                 'entity_model': models.get_model(*model.split('.')), 'entity_app_name': app_name}
        fields = getattr(self, 'get_entity_calendar_%s_fields' % period_type)(attr_name, model, app_name)
        attrs.update(fields)
        name = get_model_name(model, attr_name, period_type)
        return type(name, (getattr(base, 'EntityCalendar%s' % period_type.title()), ) + mixins, attrs)

    def get_entity_calendar_year_fields(self, attr_name, model, app_name):
        return {attr_name:  models.ForeignKey(model, related_name="%scalendaryears" % attr_name),
                'calendar_year': models.ForeignKey('dbcalendar.CalendarYear', verbose_name=u"Calendar year", related_name="%scalendaryears" % attr_name)
                }

    def get_entity_calendar_month_fields(self, attr_name, model, app_name):
        return {attr_name:  models.ForeignKey(model, related_name="%scalendarmonths" % attr_name),
                "%s_year" % attr_name:  models.ForeignKey("%s.%s" % (app_name, get_model_name(model, attr_name, 'year')), related_name="%scalendarmonths" % attr_name),
                'calendar_month': models.ForeignKey('dbcalendar.CalendarMonth', verbose_name=u"Calendar year", related_name="%scalendarmonths" % attr_name,
                                                    on_delete=models.PROTECT)
        }

    def get_entity_calendar_week_fields(self, attr_name, model, app_name):
        return {attr_name:  models.ForeignKey(model, related_name="%scalendarweeks" % attr_name),
                "%s_year" % attr_name:  models.ForeignKey("%s.%s" % (app_name, get_model_name(model, attr_name, 'year')), related_name="%scalendarweeks" % attr_name),
                'calendar_week': models.ForeignKey('dbcalendar.CalendarWeek', verbose_name=u"Calendar week", related_name="%scalendarweeks" % attr_name,
                                                   on_delete=models.PROTECT)
        }

    def get_entity_calendar_day_fields(self, attr_name, model, app_name):
        return {attr_name:  models.ForeignKey(model, related_name="%scalendardays" % attr_name),
                "%s_week" % attr_name:  models.ForeignKey("%s.%s" % (app_name, get_model_name(model, attr_name, 'week')), 
                                                          related_name="%scalendardays" % attr_name, on_delete=models.PROTECT),
                "%s_month" % attr_name:  models.ForeignKey("%s.%s" % (app_name, get_model_name(model, attr_name, 'month')), 
                                                           related_name="%scalendardays" % attr_name, on_delete=models.PROTECT),
                'calendar_day': models.ForeignKey('dbcalendar.CalendarDay', verbose_name=u"Calendar day", 
                                                  related_name="%scalendardays" % attr_name, on_delete=models.PROTECT)
        }



entity_calendar_factory = EntityCalendarFactory()
