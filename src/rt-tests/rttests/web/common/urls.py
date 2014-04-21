import django.conf.urls as urls

import rttests.web.common.views as views

urlpatterns = urls.patterns(
    '',
    urls.url(r'^$', views.index),
)
