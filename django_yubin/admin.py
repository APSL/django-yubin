from django.conf.urls import url
from django.contrib import admin, messages as dj_messages
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from kombu.exceptions import OperationalError

from . import models, tasks, settings
from .message_utils import get_attachments, get_attachment, is_part_encoded


class LogInline(admin.TabularInline):
    model = models.Log

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.id,))
        return mark_safe("""<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url)
    message_link.allow_tags = True
    message_link.short_description = _('Show')

    list_display = ('from_address', 'to_address', 'subject', 'date_created', 'date_sent',
                    'date_enqueued', 'status', 'message_link')
    list_filter = ('date_created', 'date_sent', 'date_enqueued', 'status')
    search_fields = ('to_address', 'subject', 'from_address', 'encoded_message',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    actions = ['enqueue_action', 'mark_as_sent_action', 'mark_as_created_action']
    inlines = [LogInline]

    def enqueue_action(self, request, queryset):
        if settings.PAUSE_SEND:
            msg = _("Sending emails is paused by settings, no email has been sent.")
            self.message_user(request, msg, level=dj_messages.INFO)
            return

        if queryset.count() != queryset.sendables().count():
            msg = _('Messages with "Created", "Queued" or "In process" statuses can not be enqueued.')
            self.message_user(request, msg, level=dj_messages.WARNING)
            return

        failed, queued = [], []
        for message in queryset:
            try:
                tasks.send_email.delay(message.pk)
                message.mark_as(models.Message.STATUS_QUEUED, 'Enqueued from the admin.')
                queued.append(str(message.pk))
            except OperationalError:
                failed.append(str(message.pk))

        msg = _("{queued_count} emails enqueued: {queued} | "
                "{failed_count} emails failed: {failed}".format(
                    queued_count=len(queued), queued=','.join(queued),
                    failed_count=len(failed), failed=','.join(failed),
                    )
                )
        if failed and queued:
            level = dj_messages.WARNING
        elif failed:
            level = dj_messages.ERROR
        elif queued:
            level = dj_messages.SUCCESS
        else:
            level = dj_messages.INFO

        self.message_user(request, msg, level)
    enqueue_action.short_description = _('Enqueue selected messages')

    def mark_as_sent_action(self, request, queryset):
        for message in queryset:
            message.mark_as(models.Message.STATUS_SENT, 'Marked as sent from the admin.')
        self.message_user(request, _("Emails marked as sent."), level=dj_messages.SUCCESS)
    mark_as_sent_action.short_description = _('Mark as sent selected messages')

    def mark_as_created_action(self, request, queryset):
        for message in queryset:
            message.mark_as(models.Message.STATUS_CREATED, 'Marked as created from the admin.')
        self.message_user(request, _("Emails marked as created."), level=dj_messages.SUCCESS)
    mark_as_created_action.short_description = _('Mark as created selected messages')

    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()
        custom_urls = [
            url(r'^mail/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.detail_view),
                name='mail_detail'),
            url(r'^mail/attachment/(?P<pk>\d+)/(?P<firma>[0-9a-f]{32})/$',
                self.admin_site.admin_view(self.download_view),
                name="mail_download"),
            url(r'^mail/html/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.html_view),
                name="mail_html"),
        ]
        return custom_urls + urls

    def detail_view(self, request, pk):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        context = {'subject': msg.get_subject(),
                   'from': msg.get_address('from'),
                   'to': msg.get_addresses('to'),
                   'cc': msg.get_addresses('cc'),
                   'msg_text': msg.text_part.part.get_payload(
                       decode=is_part_encoded(msg, 'text_part')) if msg.text_part else None,
                   'msg_html': msg.html_part.part.get_payload(
                       decode=is_part_encoded(msg, 'html_part')) if msg.html_part else None,
                   'attachments': get_attachments(msg),
                   'is_popup': True,
                   'object': instance}
        return render(request, 'django_yubin/message_detail.html', context)

    def download_view(self, request, pk, firma):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        arx = get_attachment(msg, key=firma)
        response = HttpResponse(content_type=arx.type)
        response['Content-Disposition'] = 'filename=' + arx.filename
        response.write(arx.payload)
        return response

    @xframe_options_sameorigin
    def html_view(self, request, pk):
        instance = models.Message.objects.get(pk=pk)
        msg = instance.get_pyz_message()
        msg.html_part.part._charset = 'utf-8'
        context = {'msg_html': msg.html_part.part.get_payload(decode=is_part_encoded(msg, 'html_part'))}
        return render(request, 'django_yubin/html_detail.html', context)


@admin.register(models.Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added')


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    def message_link(self, obj):
        url = reverse('admin:mail_detail', args=(obj.message.id,))
        return mark_safe("""<a href="%s" onclick="return showAddAnotherPopup(this);">show</a>""" % url)
    message_link.allow_tags = True
    message_link.short_description = _('Message')

    def message__to_address(self, obj):
        return obj.message.to_address
    message__to_address.admin_order_field = 'message__to_address'

    def message__subject(self, obj):
        return obj.message.subject
    message__subject.admin_order_field = 'message__subject'

    list_select_related = True
    list_display = ('id', 'action', 'message__to_address', 'message__subject', 'date', 'message_link')
    list_filter = ('action', 'date')
    list_display_links = ('id',)
    date_hierarchy = 'date'
