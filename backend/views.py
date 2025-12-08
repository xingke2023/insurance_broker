from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.http import HttpResponse

# 为前端 SPA 提供 index.html
index_view = never_cache(TemplateView.as_view(template_name='index.html'))

# 微信域名验证
def wechat_verify(request):
    """返回微信域名验证文件内容"""
    return HttpResponse('a986bf035c42edc98f14fb0cb58fb9b8', content_type='text/plain')
