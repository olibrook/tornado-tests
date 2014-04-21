import django.conf.urls as urls

import rttests.web.common.urls as common_urls

urlpatterns = urls.patterns('',
    urls.url(r'', urls.include(common_urls)),
)
