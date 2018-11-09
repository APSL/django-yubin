#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from functools import wraps

from django.conf.urls import url
from django.contrib import admin

try:
    # from django 1.10 and above
    from django.urls import reverse
except ImportError:
    # until django 1.9
    from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from django_yubin import models

from .mail_utils import get_attachments, get_attachment


class CustomViewAdminMixin(object):
    def decorate_admin_view(
        self, view, require_add_permission=False,
        require_change_permission=False, require_delete_permission=False
    ):
        """
        Add the following permission checks to a view.
        * The default admin_view decorator checks (is_staff and is_active)
        * Depending on the arguments if 'add', 'change' or 'delete' permission is
          set for this model.

        :param view View which should be decorated with permission checks.
        :param require_add_permission If a check for 'add' permission should be done.
        :param require_change_permission If a check for 'change' permission should be done.
        :param require_delete_permission If a check for 'delete' permission should be done.
        :return wrapped view
        """

        def wrap(view):
            @wraps(view)
            def wrapper(request, *args, **kwargs):
                if require_add_permission and not self.has_add_permission(request):
                    raise PermissionDenied
                if require_change_permission and not self.has_change_permission(request):
                    raise PermissionDenied
                if require_delete_permission and not self.has_delete_permission(request):
                    raise PermissionDenied
                return view(request, *args, **kwargs)
            return wrapper
        return wrap(self.admin_site.admin_view(view))


class Message(CustomViewAdminMixin, admin.ModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.id,))
        return mark_safe("""<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url)

    message_link.allow_tags = True
    message_link.short_description = u'Show'

    list_display = ('from_address', 'to_address', 'subject', 'date_created', 'date_sent', 'message_link')
    list_filter = ('date_created', 'date_sent')
    search_fields = ('to_address', 'subject', 'from_address',
                     'encoded_message',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    actions = ['re_send', ]

    def re_send(self, request, queryset):
        """
        Re sends a previus sent e-mail. The messages shouldn't be in the queue and
        is put in the NORMAL priority
        """
        messages_sent = 0
        for selected_mail in queryset:
            qm = models.QueuedMessage(message=selected_mail)
            try:
                qm.save()
                messages_sent += 1
            except IntegrityError:
                self.message_user(request, 'Message %s is already in the queue' % selected_mail.id)
        self.message_user(request, "%s messages had been re-sent" % messages_sent)
    re_send.short_description = 're-send selected emails'

    def get_urls(self):
        urls = super(Message, self).get_urls()
        custom_urls = [
            url(r'^mail/(?P<pk>\d+)/$',
                self.decorate_admin_view(self.detail_view, require_change_permission=True),
                name='mail_detail'),
            url('^mail/attachment/(?P<pk>\d+)/(?P<firma>[0-9a-f]{32})/$',
                self.decorate_admin_view(self.download_view, require_change_permission=True),
                name="mail_download"),
            url('^mail/html/(?P<pk>\d+)/$',
                self.decorate_admin_view(self.html_view, require_change_permission=True),
                name="mail_html"),
        ]
        return custom_urls + urls

    def detail_view(self, request, pk):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        context = {'subject': msg.get_subject(), 'from': msg.get_address('from'), 'to': msg.get_addresses('to'),
                   'cc': msg.get_addresses('cc'),
                   'msg_text': msg.text_part.part.get_payload(
                       decode=self.is_base64(msg, 'text_part')) if msg.text_part else None,
                   'msg_html': msg.html_part.part.get_payload(
                       decode=self.is_base64(msg, 'html_part')) if msg.html_part else None,
                   'attachments': get_attachments(msg), 'is_popup': True, 'object': instance}
        return render(request, 'django_yubin/message_detail.html', context)

    def download_view(self, request, pk, firma):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        arx = get_attachment(msg, key=firma)
        response = HttpResponse(content_type=arx.tipus)
        response['Content-Disposition'] = 'filename=' + arx.filename
        response.write(arx.payload)
        return response

    def html_view(self, request, pk):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        msg.html_part.part._charset = 'utf-8'
        context = {'msg_html': msg.html_part.part.get_payload(decode=self.is_base64(msg, 'html_part'))}
        return render(request, 'django_yubin/html_detail.html', context)

    @staticmethod
    def is_base64(msg, part='html_part'):
        """
        detect whether is a base64 encoding or not

        :param msg, part:
        :return:
        """
        if part == 'html_part':
            return any(it[1] == 'base64' for it in msg.html_part.part._headers)
        elif part == 'text_part':
            return any(it[1] == 'base64' for it in msg.text_part.part._headers)
        return False


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
        return obj.message.date_created

    message__date_created.admin_order_field = 'message__date_created'


class QueuedMessage(MessageRelatedModelAdmin):
    def not_deferred(self, obj):
        return not obj.deferred

    not_deferred.boolean = True
    not_deferred.admin_order_field = 'deferred'

    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.message.id,))
        return mark_safe("""<a href="%s" onclick="return showAddAnotherPopup(this);">%s</a>""" % (url, obj.message))

    message_link.allow_tags = True
    message_link.short_description = u'Message'

    list_display = ('id', 'message_link', 'message__to_address',
                    'message__from_address', 'message__subject',
                    'message__date_created', 'priority', 'not_deferred')
    list_filter = ('priority', 'deferred')


class Blacklist(admin.ModelAdmin):
    list_display = ('email', 'date_added')


class Log(MessageRelatedModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.message.id,))
        return mark_safe("""<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url)

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
