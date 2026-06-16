from django.db import models
from django.contrib.auth.models import User


# 07-dars: Loyiha modelini tuzish
# 06-darsdagi yagona (flat) News modelini bu yerda to'liq,
# bog'lanishli (relational) modelga aylantiramiz.


class Category(models.Model):
    """Yangiliklar bo'limlari: Sport, Texnologiya, Iqtisod va h.k."""

    name = models.CharField("Nomi", max_length=100)
    slug = models.SlugField("Slug (URL nomi)", max_length=120, unique=True)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class News(models.Model):
    """Asosiy yangilik (maqola) modeli."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        PUBLISHED = "published", "Chop etilgan"

    title = models.CharField("Sarlavha", max_length=200)
    slug = models.SlugField("Slug (URL nomi)", max_length=220, unique=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Kategoriya",
        on_delete=models.CASCADE,
        related_name="news",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Muallif",
        on_delete=models.CASCADE,
        related_name="news",
    )
    image = models.ImageField("Rasm", upload_to="news/images/", blank=True, null=True)
    content = models.TextField("Matn")
    status = models.CharField(
        "Holati",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    views = models.PositiveIntegerField("Ko'rishlar soni", default=0)
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan vaqti", auto_now=True)

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Yangilikka yozilgan izohlar."""

    news = models.ForeignKey(
        News,
        verbose_name="Yangilik",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        User,
        verbose_name="Foydalanuvchi",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField("Izoh matni")
    created_at = models.DateTimeField("Yozilgan vaqti", auto_now_add=True)

    class Meta:
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.news}"
