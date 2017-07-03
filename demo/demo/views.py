#!/usr/bin/env python
# encoding: utf-8
# ----------------------------------------------------------------------------

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'
