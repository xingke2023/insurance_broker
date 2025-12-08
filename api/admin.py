from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import InsurancePolicy, PlanDocument, AnnualValue, MembershipPlan, UserQuota, GeminiUsage, MediaLibrary, InsuranceCompany, InsuranceCompanyRequest
import json


@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ['policy_number', 'customer_name', 'policy_type', 'premium', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'policy_type', 'created_at']
    search_fields = ['policy_number', 'customer_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(PlanDocument)
class PlanDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'user_display', 'insured_name', 'insurance_company', 'status', 'content_preview', 'created_at']
    list_filter = ['status', 'insurance_company', 'created_at']
    search_fields = ['file_name', 'insured_name', 'insurance_company', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'content_display']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'file_name', 'file_path', 'file_size', 'status', 'error_message')
        }),
        ('受保人信息', {
            'fields': ('insured_name', 'insured_age', 'insured_gender')
        }),
        ('保险产品信息', {
            'fields': ('insurance_product', 'insurance_company')
        }),
        ('保费信息', {
            'fields': ('annual_premium', 'payment_years', 'total_premium', 'insurance_period', 'sum_assured')
        }),
        ('OCR识别内容', {
            'fields': ('content_display',),
            'classes': ('collapse',)  # 默认折叠
        }),
        ('提取数据', {
            'fields': ('extracted_data',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_display(self, obj):
        """显示用户"""
        if obj.user:
            return obj.user.username
        return '-'
    user_display.short_description = '上传用户'

    def content_preview(self, obj):
        """内容预览"""
        if obj.content:
            preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
            return format_html('<span style="color: #666;">{}</span>', preview)
        return '-'
    content_preview.short_description = '内容预览'

    def content_display(self, obj):
        """完整内容显示"""
        if obj.content:
            return format_html('<pre style="white-space: pre-wrap; word-wrap: break-word; max-height: 500px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', obj.content)
        return '-'
    content_display.short_description = '完整OCR内容'


@admin.register(AnnualValue)
class AnnualValueAdmin(admin.ModelAdmin):
    list_display = ['plan_document', 'policy_year', 'guaranteed_cash_value', 'non_guaranteed_cash_value', 'total_cash_value', 'created_at']
    list_filter = ['plan_document', 'created_at']
    search_fields = ['plan_document__file_name', 'plan_document__insured_name']
    ordering = ['plan_document', 'policy_year']


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_id', 'price_display', 'duration', 'features_display', 'badge', 'is_popular', 'is_active', 'sort_order']
    list_filter = ['is_active', 'is_popular', 'created_at']
    search_fields = ['name', 'plan_id']
    ordering = ['sort_order', 'id']

    fieldsets = (
        ('基本信息', {
            'fields': ('plan_id', 'name', 'price', 'original_price', 'duration')
        }),
        ('套餐权益', {
            'fields': ('features',),
            'description': '权益列表，每行一个权益，例如：<br>["IP形象生成1000次", "文案配图生成1000次", "永久有效", "按需使用"]'
        }),
        ('显示设置', {
            'fields': ('badge', 'is_popular', 'discount_info', 'sort_order', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def price_display(self, obj):
        """价格显示"""
        if obj.original_price:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">¥{}</span> '
                '<span style="color: #999; text-decoration: line-through;">¥{}</span>',
                obj.price, obj.original_price
            )
        return format_html('<span style="color: #27ae60; font-weight: bold;">¥{}</span>', obj.price)
    price_display.short_description = '价格'

    def features_display(self, obj):
        """权益显示"""
        if obj.features:
            features_html = '<br>'.join([f'• {f}' for f in obj.features])
            return format_html('<div style="line-height: 1.8;">{}</div>', features_html)
        return '-'
    features_display.short_description = '包含权益'


@admin.register(UserQuota)
class UserQuotaAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'available_quota_display', 'total_purchased_display', 'last_used', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__wechatuser__nickname']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('额度信息', {
            'fields': ('available_quota', 'total_purchased'),
            'description': '可以直接修改"可用额度"来增加或减少用户的调用次数'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/userquota_admin.css',)
        }

    def user_display(self, obj):
        """显示用户信息"""
        if obj.user:
            try:
                wechat_user = obj.user.wechatuser
                return format_html(
                    '<strong>{}</strong><br><span style="color: #666; font-size: 0.9em;">{}</span>',
                    obj.user.username,
                    wechat_user.nickname if wechat_user.nickname else '未设置昵称'
                )
            except:
                return obj.user.username
        return '-'
    user_display.short_description = '用户'

    def available_quota_display(self, obj):
        """可用额度显示（带颜色）"""
        if obj.available_quota <= 0:
            color = '#e74c3c'  # 红色
            icon = '❌'
        elif obj.available_quota <= 10:
            color = '#f39c12'  # 橙色
            icon = '⚠️'
        else:
            color = '#27ae60'  # 绿色
            icon = '✅'

        return format_html(
            '<div style="text-align: right;"><span style="color: {}; font-weight: bold; font-size: 1.1em;">{} {} 次</span></div>',
            color, icon, obj.available_quota
        )
    available_quota_display.short_description = '可用额度'

    def total_purchased_display(self, obj):
        """累计购买显示（右对齐）"""
        return format_html(
            '<div style="text-align: right;"><span style="color: #666; font-size: 1em;">{} 次</span></div>',
            obj.total_purchased
        )
    total_purchased_display.short_description = '累计购买'

    def last_used(self, obj):
        """最后使用时间"""
        last_usage = GeminiUsage.objects.filter(user=obj.user, success=True).order_by('-created_at').first()
        if last_usage:
            return last_usage.created_at.strftime('%Y-%m-%d %H:%M')
        return '从未使用'
    last_used.short_description = '最后使用'

    actions = ['add_10_quota', 'add_50_quota', 'add_100_quota', 'reset_to_3_quota']

    def add_10_quota(self, request, queryset):
        """批量增加10次额度"""
        count = 0
        for quota in queryset:
            quota.add_quota(10)
            count += 1
        self.message_user(request, f'成功为 {count} 个用户增加了 10 次额度')
    add_10_quota.short_description = '➕ 增加 10 次额度'

    def add_50_quota(self, request, queryset):
        """批量增加50次额度"""
        count = 0
        for quota in queryset:
            quota.add_quota(50)
            count += 1
        self.message_user(request, f'成功为 {count} 个用户增加了 50 次额度')
    add_50_quota.short_description = '➕ 增加 50 次额度'

    def add_100_quota(self, request, queryset):
        """批量增加100次额度"""
        count = 0
        for quota in queryset:
            quota.add_quota(100)
            count += 1
        self.message_user(request, f'成功为 {count} 个用户增加了 100 次额度')
    add_100_quota.short_description = '➕ 增加 100 次额度'

    def reset_to_3_quota(self, request, queryset):
        """批量重置为3次额度"""
        count = queryset.update(available_quota=3)
        self.message_user(request, f'成功为 {count} 个用户重置额度为 3 次')
    reset_to_3_quota.short_description = '🔄 重置为 3 次额度'


@admin.register(GeminiUsage)
class GeminiUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'generation_type_display', 'success_display', 'prompt_preview', 'created_at']
    list_filter = ['generation_type', 'success', 'created_at']
    search_fields = ['user__username', 'user__wechatuser__nickname', 'prompt', 'error_message']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['user', 'generation_type', 'prompt', 'success', 'error_message', 'created_at']

    fieldsets = (
        ('使用信息', {
            'fields': ('user', 'generation_type', 'success')
        }),
        ('请求内容', {
            'fields': ('prompt',),
            'classes': ('collapse',)
        }),
        ('错误信息', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )

    def user_display(self, obj):
        """显示用户"""
        if obj.user:
            try:
                wechat_user = obj.user.wechatuser
                return format_html(
                    '{}<br><span style="color: #666; font-size: 0.85em;">{}</span>',
                    obj.user.username,
                    wechat_user.nickname if wechat_user.nickname else ''
                )
            except:
                return obj.user.username
        return '-'
    user_display.short_description = '用户'

    def generation_type_display(self, obj):
        """生成类型显示"""
        type_map = {
            'ip_image': 'IP形象',
            'content_image': '内容配图'
        }
        type_name = type_map.get(obj.generation_type, obj.generation_type)
        return format_html('<span style="padding: 2px 8px; background: #3498db; color: white; border-radius: 3px; font-size: 0.85em;">{}</span>', type_name)
    generation_type_display.short_description = '类型'

    def success_display(self, obj):
        """成功状态显示"""
        if obj.success:
            return format_html('<span style="color: #27ae60; font-weight: bold;">✅ 成功</span>')
        else:
            error_preview = obj.error_message[:30] + '...' if obj.error_message and len(obj.error_message) > 30 else obj.error_message or ''
            return format_html('<span style="color: #e74c3c; font-weight: bold;">❌ 失败</span><br><span style="color: #999; font-size: 0.85em;">{}</span>', error_preview)
    success_display.short_description = '状态'

    def prompt_preview(self, obj):
        """提示词预览"""
        if obj.prompt:
            preview = obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
            return format_html('<span style="color: #666; font-size: 0.9em;">{}</span>', preview)
        return '-'
    prompt_preview.short_description = '提示词'

    def has_add_permission(self, request):
        """禁止手动添加记录"""
        return False

    def has_delete_permission(self, request, obj=None):
        """允许删除记录（清理历史数据）"""
        return True


@admin.register(MediaLibrary)
class MediaLibraryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'media_type_display', 'image_thumbnail', 'prompt_preview', 'size_display', 'is_favorite', 'created_at']
    list_filter = ['media_type', 'is_favorite', 'created_at']
    search_fields = ['user__username', 'user__wechatuser__nickname', 'prompt']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['user', 'media_type', 'original_url', 'local_path', 'image_preview', 'width', 'height', 'file_size', 'created_at', 'updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'media_type', 'is_favorite')
        }),
        ('图片信息', {
            'fields': ('image_preview', 'original_url', 'local_path', 'width', 'height', 'file_size')
        }),
        ('描述信息', {
            'fields': ('prompt', 'related_ip_image_id')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_display(self, obj):
        """显示用户"""
        if obj.user:
            try:
                wechat_user = obj.user.wechatuser
                return format_html(
                    '{}<br><span style="color: #666; font-size: 0.85em;">{}</span>',
                    obj.user.username,
                    wechat_user.nickname if wechat_user.nickname else ''
                )
            except:
                return obj.user.username
        return '-'
    user_display.short_description = '用户'

    def media_type_display(self, obj):
        """媒体类型显示"""
        type_colors = {
            'ip_image': '#9b59b6',
            'content_image': '#3498db'
        }
        color = type_colors.get(obj.media_type, '#95a5a6')
        return format_html(
            '<span style="padding: 3px 10px; background: {}; color: white; border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_media_type_display()
        )
    media_type_display.short_description = '类型'

    def image_thumbnail(self, obj):
        """缩略图显示"""
        if obj.local_path:
            url = f"/media/{obj.local_path}"
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />', url)
        elif obj.original_url:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />', obj.original_url)
        return '-'
    image_thumbnail.short_description = '预览'

    def image_preview(self, obj):
        """大图预览"""
        if obj.local_path:
            url = f"/media/{obj.local_path}"
            return format_html('<img src="{}" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />', url)
        elif obj.original_url:
            return format_html('<img src="{}" style="max-width: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />', obj.original_url)
        return '-'
    image_preview.short_description = '图片预览'

    def prompt_preview(self, obj):
        """提示词预览"""
        if obj.prompt:
            preview = obj.prompt[:40] + '...' if len(obj.prompt) > 40 else obj.prompt
            return format_html('<span style="color: #666; font-size: 0.9em;">{}</span>', preview)
        return '-'
    prompt_preview.short_description = '提示词'

    def size_display(self, obj):
        """文件大小显示"""
        if obj.file_size:
            size_kb = obj.file_size / 1024
            if size_kb > 1024:
                return f"{size_kb/1024:.1f} MB"
            return f"{size_kb:.1f} KB"
        return '-'
    size_display.short_description = '大小'

    def has_add_permission(self, request):
        """禁止手动添加记录"""
        return False

    actions = ['mark_as_favorite', 'unmark_as_favorite']

    def mark_as_favorite(self, request, queryset):
        """标记为收藏"""
        count = queryset.update(is_favorite=True)
        self.message_user(request, f'成功标记 {count} 个素材为收藏')
    mark_as_favorite.short_description = '⭐ 标记为收藏'

    def unmark_as_favorite(self, request, queryset):
        """取消收藏"""
        count = queryset.update(is_favorite=False)
        self.message_user(request, f'成功取消 {count} 个素材的收藏')
    unmark_as_favorite.short_description = '⭐ 取消收藏'


# ============ 保险公司接口配置管理 ============

class InsuranceCompanyRequestInline(admin.TabularInline):
    """保险公司请求配置内联显示"""
    model = InsuranceCompanyRequest
    extra = 0
    fields = ['request_name', 'request_url', 'insurance_product', 'requires_bearer_token', 'is_active', 'sort_order']
    readonly_fields = []
    show_change_link = True


@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    """保险公司管理"""
    list_display = ['code', 'name', 'name_en', 'icon_display', 'color_display', 'request_count', 'is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'name_en']
    ordering = ['sort_order', 'id']

    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'name_en', 'description'),
            'description': '保险公司的基本标识信息'
        }),
        ('显示设置', {
            'fields': ('icon', 'color_gradient', 'bg_color'),
            'description': '用于前端界面显示的样式配置<br>'
                         '• 图标(icon): 可以输入Emoji表情符号（如：🏦）或公司Logo的URL地址（如：https://example.com/logo.png 或 /media/logos/company.png）<br>'
                         '• 前端会自动识别：URL格式显示为图片，其他显示为文本图标'
        }),
        ('API配置', {
            'fields': ('headers', 'bearer_token', 'cookie'),
            'description': '<strong>API调用所需的配置信息</strong><br>'
                         '• Headers: 公司级别的通用HTTP Headers，会应用到该公司的所有API请求<br>'
                         '• Bearer Token: 用于Authorization请求头<br>'
                         '• Cookie: 用于Cookie请求头<br>'
                         '• 这些信息将用于调用保险公司的API接口',
            'classes': ('collapse',)  # 默认折叠，保护敏感信息
        }),
        ('标准退保数据', {
            'fields': ('standard_surrender_policy',),
            'description': '<strong>标准退保数据配置</strong><br>'
                         '• 格式: JSON字符串<br>'
                         '• 示例: {"standard": [{"policy_year": 1, "guaranteed": 0, "non_guaranteed": 0, "total": 0, "premiums_paid": 10000}, {"policy_year": 2, "guaranteed": 2500, "non_guaranteed": 19200, "total": 21700, "premiums_paid": 20000}]}<br>'
                         '• 字段说明：<br>'
                         '  - policy_year: 保单年度<br>'
                         '  - guaranteed: 保证现金价值<br>'
                         '  - non_guaranteed: 非保证现金价值<br>'
                         '  - total: 总现金价值（预期价值）<br>'
                         '  - premiums_paid: 已缴保费（累计）<br>'
                         '• 包含第1年到第100年的标准退保价值数据',
            'classes': ('collapse',)
        }),
        ('状态与排序', {
            'fields': ('is_active', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    inlines = [InsuranceCompanyRequestInline]

    def icon_display(self, obj):
        """图标显示"""
        if obj.icon:
            return format_html('<span style="font-size: 1.5em;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = '图标'

    def color_display(self, obj):
        """颜色显示"""
        if obj.color_gradient:
            return format_html(
                '<div style="background: linear-gradient(135deg, {}); width: 100px; height: 30px; border-radius: 4px;"></div>',
                obj.color_gradient.replace('from-', '#').replace('to-', ', #')[:50]  # 简化显示
            )
        return '-'
    color_display.short_description = '颜色'

    def request_count(self, obj):
        """请求数量"""
        count = InsuranceCompanyRequest.objects.filter(company=obj).count()
        if count > 0:
            return format_html('<span style="color: #27ae60; font-weight: bold;">{} 个</span>', count)
        return format_html('<span style="color: #999;">0 个</span>')
    request_count.short_description = '接口数量'


class InsuranceCompanyRequestForm(forms.ModelForm):
    """自定义表单，使用更好的JSON编辑器"""

    headers_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'style': 'width: 100%; font-family: monospace; font-size: 13px;'
        }),
        required=False,
        label='HTTP Headers',
        help_text='HTTP请求头配置，可以是JSON格式或任意文本格式。推荐JSON格式: {"Content-Type": "application/json", "Accept": "application/json"}'
    )

    request_template_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 20,
            'style': 'width: 100%; font-family: monospace; font-size: 13px;'
        }),
        required=False,
        label='POST Request 模板 (JSON格式)',
        help_text='请输入JSON格式的请求体模板。使用 {{变量名}} 表示可配置项，例如: {{premium}}, {{bearer_token}}'
    )

    configurable_fields_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'style': 'width: 100%; font-family: monospace; font-size: 13px;'
        }),
        required=False,
        label='可配置字段列表 (JSON数组)',
        help_text='例如: ["premium", "withdrawal_amount", "bearer_token"]'
    )

    field_descriptions_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'style': 'width: 100%; font-family: monospace; font-size: 13px;'
        }),
        required=False,
        label='字段描述配置 (JSON对象)',
        help_text='例如: {"premium": {"label": "每期保费", "type": "number", "required": true, "default": 10000}}'
    )

    response_template_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'style': 'width: 100%; font-family: monospace; font-size: 13px;'
        }),
        required=False,
        label='Response 响应模板 (JSON格式，可选)',
        help_text='预期的响应格式示例，用于文档说明'
    )

    class Meta:
        model = InsuranceCompanyRequest
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # 加载现有数据
            if self.instance.headers:
                # 处理headers字段（可能是字符串、字典或键值对格式）
                headers_data = self.instance.headers
                if isinstance(headers_data, str):
                    headers_str = headers_data.strip()
                    if headers_str:
                        try:
                            # 尝试解析为JSON
                            headers_data = json.loads(headers_str)
                            # 如果是JSON，格式化显示
                            self.fields['headers_text'].initial = json.dumps(
                                headers_data,
                                indent=2,
                                ensure_ascii=False
                            )
                        except json.JSONDecodeError:
                            # 如果不是JSON，直接显示原始字符串
                            self.fields['headers_text'].initial = headers_str
                    else:
                        self.fields['headers_text'].initial = ''
                else:
                    # 如果已经是字典，格式化显示
                    self.fields['headers_text'].initial = json.dumps(
                        headers_data,
                        indent=2,
                        ensure_ascii=False
                    )
            if self.instance.request_template:
                self.fields['request_template_text'].initial = json.dumps(
                    self.instance.request_template,
                    indent=2,
                    ensure_ascii=False
                )
            if self.instance.configurable_fields:
                self.fields['configurable_fields_text'].initial = json.dumps(
                    self.instance.configurable_fields,
                    indent=2,
                    ensure_ascii=False
                )
            if self.instance.field_descriptions:
                self.fields['field_descriptions_text'].initial = json.dumps(
                    self.instance.field_descriptions,
                    indent=2,
                    ensure_ascii=False
                )
            if self.instance.response_template:
                self.fields['response_template_text'].initial = json.dumps(
                    self.instance.response_template,
                    indent=2,
                    ensure_ascii=False
                )

    def clean_headers_text(self):
        """验证并转换headers（支持JSON或纯文本）"""
        text = self.cleaned_data.get('headers_text', '').strip()
        if text:
            # 尝试解析为JSON
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    # 如果是有效的JSON对象，返回JSON字符串
                    return json.dumps(data, ensure_ascii=False)
                else:
                    # 如果解析结果不是对象，作为纯文本返回
                    return text
            except json.JSONDecodeError:
                # 如果不是有效的JSON，直接作为纯文本返回
                return text
        return ''

    def clean_request_template_text(self):
        """验证并转换请求模板JSON"""
        text = self.cleaned_data.get('request_template_text', '').strip()
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f'JSON格式错误: {str(e)}')
        return {}

    def clean_configurable_fields_text(self):
        """验证并转换可配置字段JSON"""
        text = self.cleaned_data.get('configurable_fields_text', '').strip()
        if text:
            try:
                data = json.loads(text)
                if not isinstance(data, list):
                    raise forms.ValidationError('必须是JSON数组格式')
                return data
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f'JSON格式错误: {str(e)}')
        return []

    def clean_field_descriptions_text(self):
        """验证并转换字段描述JSON"""
        text = self.cleaned_data.get('field_descriptions_text', '').strip()
        if text:
            try:
                data = json.loads(text)
                if not isinstance(data, dict):
                    raise forms.ValidationError('必须是JSON对象格式')
                return data
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f'JSON格式错误: {str(e)}')
        return {}

    def clean_response_template_text(self):
        """验证并转换响应模板JSON"""
        text = self.cleaned_data.get('response_template_text', '').strip()
        if text:
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f'JSON格式错误: {str(e)}')
        return {}

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 保存JSON数据到模型字段
        instance.headers = self.cleaned_data.get('headers_text', {})
        instance.request_template = self.cleaned_data.get('request_template_text', {})
        instance.configurable_fields = self.cleaned_data.get('configurable_fields_text', [])
        instance.field_descriptions = self.cleaned_data.get('field_descriptions_text', {})
        instance.response_template = self.cleaned_data.get('response_template_text', {})

        if commit:
            instance.save()
        return instance


@admin.register(InsuranceCompanyRequest)
class InsuranceCompanyRequestAdmin(admin.ModelAdmin):
    """保险公司接口请求配置管理"""
    form = InsuranceCompanyRequestForm

    list_display = [
        'request_name',
        'company_display',
        'request_method',
        'url_display',
        'product_display',
        'token_required',
        'configurable_count',
        'is_active',
        'sort_order'
    ]
    list_filter = ['company', 'request_method', 'requires_bearer_token', 'is_active', 'created_at']
    search_fields = ['request_name', 'request_url', 'insurance_product', 'company__name']
    ordering = ['company__sort_order', 'sort_order', 'id']

    fieldsets = (
        ('基本信息', {
            'fields': ('company', 'request_name', 'insurance_product'),
            'description': '请求的基本标识信息'
        }),
        ('API配置', {
            'fields': ('request_url', 'request_method', 'requires_bearer_token'),
            'description': '接口的URL和请求方法'
        }),
        ('HTTP Headers', {
            'fields': ('headers_text',),
            'description': '<strong>HTTP请求头配置</strong><br>'
                         '• <strong>推荐</strong>使用JSON对象格式，例如:<br>'
                         '<pre>{\n'
                         '  "Content-Type": "application/json",\n'
                         '  "Accept": "application/json, text/plain, */*",\n'
                         '  "Language": "zh-Hant",\n'
                         '  "X-Compcode": "AXAHK"\n'
                         '}</pre>'
                         '• 也可以输入任意文本格式<br>'
                         '• Authorization和Cookie会从公司配置或用户输入自动添加，无需在这里配置'
        }),
        ('POST Request 模板', {
            'fields': ('request_template_text',),
            'description': '<strong>在这里输入完整的POST请求体JSON</strong><br>'
                         '• 使用 <code>{{变量名}}</code> 表示可配置字段<br>'
                         '• 例如: <code>{"premium": "{{premium}}", "amount": "{{withdrawal_amount}}"}</code><br>'
                         '• 系统会自动替换这些占位符为实际值'
        }),
        ('可配置字段', {
            'fields': ('configurable_fields_text',),
            'description': '<strong>定义哪些字段可以配置</strong><br>'
                         '• JSON数组格式: <code>["premium", "withdrawal_amount", "bearer_token"]</code><br>'
                         '• 这些字段名必须与POST Request模板中的 {{变量名}} 对应'
        }),
        ('字段描述', {
            'fields': ('field_descriptions_text',),
            'description': '<strong>描述每个可配置字段的属性</strong><br>'
                         '• JSON对象格式，每个字段包含: label(标签), type(类型), required(必填), default(默认值)<br>'
                         '• 例如: <pre>{\n'
                         '  "premium": {\n'
                         '    "label": "每期保费",\n'
                         '    "type": "number",\n'
                         '    "required": true,\n'
                         '    "default": 10000\n'
                         '  }\n'
                         '}</pre>'
        }),
        ('Response 模板 (可选)', {
            'fields': ('response_template_text',),
            'description': '预期的响应格式示例，用于前端参考（可选）',
            'classes': ('collapse',)
        }),
        ('状态与排序', {
            'fields': ('is_active', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def company_display(self, obj):
        """保险公司显示"""
        if obj.company:
            return format_html(
                '<span style="font-size: 1.2em;">{}</span> {}',
                obj.company.icon or '🏢',
                obj.company.name
            )
        return '-'
    company_display.short_description = '保险公司'

    def url_display(self, obj):
        """URL显示（截断）"""
        if obj.request_url:
            url = obj.request_url
            if len(url) > 50:
                url = url[:47] + '...'
            return format_html('<code style="font-size: 0.85em; color: #2c3e50;">{}</code>', url)
        return '-'
    url_display.short_description = 'API URL'

    def product_display(self, obj):
        """产品名称显示"""
        if obj.insurance_product:
            return format_html('<span style="color: #666; font-size: 0.9em;">{}</span>', obj.insurance_product)
        return '-'
    product_display.short_description = '保险产品'

    def token_required(self, obj):
        """是否需要token"""
        if obj.requires_bearer_token:
            return format_html('<span style="color: #e74c3c; font-weight: bold;">🔐 需要</span>')
        return format_html('<span style="color: #95a5a6;">否</span>')
    token_required.short_description = 'Bearer Token'

    def configurable_count(self, obj):
        """可配置字段数量"""
        count = len(obj.configurable_fields) if obj.configurable_fields else 0
        if count > 0:
            return format_html('<span style="color: #3498db; font-weight: bold;">{} 个</span>', count)
        return format_html('<span style="color: #999;">0 个</span>')
    configurable_count.short_description = '可配置字段'

    class Media:
        css = {
            'all': ('admin/css/insurance_company_admin.css',)
        }
        js = ('admin/js/insurance_company_admin.js',)
