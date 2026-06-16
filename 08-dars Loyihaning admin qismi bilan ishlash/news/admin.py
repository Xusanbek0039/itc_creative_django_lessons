from django.contrib import admin
from django.utils.html import format_html
from .models import Category, News, Comment


# 08-dars: Loyihaning admin qismi bilan ishlash
# Admin panelni o'zimizga moslab, kuchli boshqaruv interfeysiga aylantiramiz.


# --- Admin sayt sarlavhalarini o'zgartiramiz ---
admin.site.site_header = "ITC-Blog boshqaruv paneli"
admin.site.site_title = "ITC-Blog admin"
admin.site.index_title = "Boshqaruv bo'limi"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "news_count", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)

    @admin.display(description="Yangiliklar soni")
    def news_count(self, obj):
        return obj.news.count()


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "author", "status_badge", "views", "created_at",
    )
    list_display_links = ("title",)
    list_editable = ("category",)
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at", "views")
    inlines = [CommentInline]

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": ("title", "slug", "category", "author"),
        }),
        ("Kontent", {
            "fields": ("image", "content", "status"),
        }),
        ("Statistika", {
            "classes": ("collapse",),
            "fields": ("views", "created_at", "updated_at"),
        }),
    )

    @admin.display(description="Holati", ordering="status")
    def status_badge(self, obj):
        color = "#10B981" if obj.status == News.Status.PUBLISHED else "#F59E0B"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:8px;font-size:11px;">{}</span>',
            color, obj.get_status_display(),
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "news", "short_body", "created_at")
    search_fields = ("body",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    @admin.display(description="Izoh")
    def short_body(self, obj):
        return (obj.body[:50] + "...") if len(obj.body) > 50 else obj.body
