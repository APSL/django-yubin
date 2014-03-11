#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from django.contrib import admin
from django_yubin import models
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import *
from mail_utils import get_attachments, get_attachment
from pyzmail.parse import message_from_string
from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse


class Message(admin.ModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.id,))
        return """<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url
    message_link.allow_tags = True
    message_link.short_description = u'Show'

    list_display = ('from_address', 'to_address', 'subject', 'date_created', 'message_link')
    list_filter = ('date_created',)
    search_fields = ('to_address', 'subject', 'from_address',
            'encoded_message',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)

    def get_urls(self):
        urls = super(Message, self).get_urls()
        custom_urls = patterns('',
            url(r'^mail/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.detail_view),
                name='mail_detail'),
            url('^mail/attachment/(?P<pk>\d+)/(?P<firma>[0-9a-f]{32})/$',
                self.admin_site.admin_view(self.download_view),
                name="mail_download"),
            url('^mail/html/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.html_view),
                name="mail_html"))
        return custom_urls + urls

    def detail_view(self, request, pk):
        instance = models.Message.objects.get(pk=pk)
        payload_str = instance.encoded_message.encode('utf-8')
        msg = message_from_string(payload_str)
        context = {}
        context['subject'] = msg.get_subject()
        context['from'] = msg.get_address('from')
        context['to'] = msg.get_addresses('to')
        context['cc'] = msg.get_addresses('cc')
        msg_text = msg.text_part.get_payload() if msg.text_part else None
        msg_html = msg.html_part.get_payload() if msg.html_part else None
        context['msg_html'] = msg_html
        context['msg_text'] = msg_text
        context['attachments'] = get_attachments(msg)
        context['is_popup'] = True
        context['object'] = instance
        return render(request, 'django_yubin/message_detail.html', context)

    def download_view(self, request, pk, firma):
        payload_str = models.Message.objects.get(
                pk=pk).encoded_message.encode('utf-8')
        msg = message_from_string(payload_str)
        arx = get_attachment(msg, key=firma)
        response = HttpResponse(mimetype=arx.tipus)
        response['Content-Disposition'] = 'filename=' + arx.filename
        response.write(arx.payload)
        return response

    def html_view(self, request, pk):
        msg = models.Message.objects.get(pk=pk)
        payload_str = msg.encoded_message.encode('utf-8')
        msg = message_from_string(payload_str)
        msg_html = msg.html_part.get_payload() if msg.html_part else None
        context = {}
        context['msg_html'] = msg_html
        return render(request, 'django_yubin/html_detail.html', context)

class MessageRelatedModelAdmin(admin.ModelAdmin):
    list_select_related = True

    def message__to_address(self, obj):
        return obj.message.to_address
    message__to_address.admin_order_field = 'message__to_address'

    def message__from_address(self, obj):
        return obj.message.from_address
    message__from_address.admin_order_field = 'message__from_address'

    def message__subject(self, obj):
        return obj.message.subject
    message__subject.admin_order_field = 'message__subject'

    def message__date_created(self, obj):
        return obj.message.to_address
    message__date_created.admin_order_field = 'message__date_created'


class QueuedMessage(MessageRelatedModelAdmin):
    def not_deferred(self, obj):
        return not obj.deferred
    not_deferred.boolean = True
    not_deferred.admin_order_field = 'deferred'

    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.message.id,))
        return """<a href="%s" onclick="return showAddAnotherPopup(this);">%s</a>""" % (url, obj.message)
    message_link.allow_tags = True
    message_link.short_description = u'Message'

    list_display = ('id', 'message_link', 'message__to_address',
            'message__from_address', 'message__subject',
            'message__date_created', 'priority', 'not_deferred')


class Blacklist(admin.ModelAdmin):
    list_display = ('email', 'date_added')


class Log(MessageRelatedModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.message.id,))
        return """<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url
    message_link.allow_tags = True
    message_link.short_description = u'Message'

    list_display = ('id', 'result', 'message__to_address', 'message__subject',
                    'date', 'message_link')
    list_filter = ('result',)
    list_display_links = ('id', 'result')


admin.site.register(models.Message, Message)
admin.site.register(models.QueuedMessage, QueuedMessage)
admin.site.register(models.Blacklist, Blacklist)
admin.site.register(models.Log, Log)
