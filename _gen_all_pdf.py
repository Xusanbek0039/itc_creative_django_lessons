# -*- coding: utf-8 -*-
"""01-06 darslar uchun brendlangan PDF qo'llanmalar generatori.
Tayyorladi: Husan Suyunov - IT Shaharcha, Zomin tumani filiali."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    NextPageTemplate, PageBreak, Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(ROOT, "it shaharcha.png")

INDIGO   = colors.HexColor("#4338CA")
INDIGO_D = colors.HexColor("#312E81")
VIOLET   = colors.HexColor("#7C3AED")
SKY      = colors.HexColor("#0EA5E9")
EMERALD  = colors.HexColor("#10B981")
AMBER    = colors.HexColor("#F59E0B")
ROSE     = colors.HexColor("#E11D48")
INK      = colors.HexColor("#1E293B")
SLATE    = colors.HexColor("#475569")
MUTED    = colors.HexColor("#64748B")
LIGHT    = colors.HexColor("#F1F5F9")
CODE_BG  = colors.HexColor("#0F172A")
CODE_FG  = colors.HexColor("#E2E8F0")
CARD_BG  = colors.HexColor("#EEF2FF")
LINE     = colors.HexColor("#CBD5E1")

# rang -> ochiq fon (callout/table uchun)
TINT = {
    INDIGO: CARD_BG, VIOLET: CARD_BG, SKY: colors.HexColor("#F0F9FF"),
    EMERALD: colors.HexColor("#ECFDF5"), AMBER: colors.HexColor("#FFFBEB"),
    ROSE: colors.HexColor("#FFF1F2"),
}
CYCLE = [EMERALD, INDIGO, SKY, AMBER, VIOLET, EMERALD, SKY, AMBER]

PAGE_W, PAGE_H = A4
MX = 18 * mm
W = PAGE_W - 2 * MX

ss = getSampleStyleSheet()

def style(name, **kw):
    kw.setdefault("parent", ss["Normal"])
    return ParagraphStyle(name, **kw)

BODY = style("BODY", fontName="Helvetica", fontSize=10.5, leading=16,
             textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6)
CODE = style("CODE", fontName="Courier", fontSize=8.7, leading=12.6, textColor=CODE_FG)
SMALL = style("SMALL", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED)
TH = style("TH", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.white)
TD = style("TD", fontName="Helvetica", fontSize=9.3, leading=12.5, textColor=INK)
TDC = style("TDC", fontName="Courier", fontSize=8.6, leading=12.5, textColor=INDIGO_D)


class HR(Flowable):
    def __init__(self, w, color=LINE, thick=0.8):
        super().__init__(); self.w = w; self.color = color; self.thick = thick
    def wrap(self, *a): return (self.w, self.thick + 4)
    def draw(self):
        self.canv.setStrokeColor(self.color); self.canv.setLineWidth(self.thick)
        self.canv.line(0, 2, self.w, 2)


class Badge(Flowable):
    def __init__(self, text, color, w, h=22):
        super().__init__(); self.text = text; self.color = color; self.w = w; self.h = h
    def wrap(self, *a): return (self.w, self.h + 6)
    def draw(self):
        c = self.canv
        c.setFillColor(self.color); c.roundRect(0, 0, 5, self.h, 0, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 12.5); c.drawString(12, self.h/2 - 4.5, self.text)


def code_block(lines):
    txt = "<br/>".join(
        l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
         .replace(" ", "&nbsp;") for l in lines)
    t = Table([[Paragraph(txt, CODE)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return t


def callout(title, body, color):
    inner = [Paragraph(title, style("ct", fontName="Helvetica-Bold",
                                    fontSize=10.5, leading=14, textColor=color))]
    for b in body:
        inner.append(Paragraph(b, style("cb", parent=BODY, alignment=TA_LEFT,
                                        spaceAfter=2, fontSize=10, leading=14)))
    t = Table([[inner]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT.get(color, LIGHT)),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, -1), 4, color), ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return t


def kv_table(rows, head_color):
    data = [[Paragraph(rows[0][0], TH), Paragraph(rows[0][1], TH)]]
    for k, v in rows[1:]:
        data.append([Paragraph(k, TDC), Paragraph(v, TD)])
    t = Table(data, colWidths=[W*0.34, W*0.66])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), head_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT.get(head_color, LIGHT)]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [6, 6, 0, 0]),
    ]))
    return t


def make_header_footer(num):
    def hf(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(INDIGO_D); canvas.rect(0, PAGE_H - 9, PAGE_W, 9, fill=1, stroke=0)
        canvas.setFillColor(VIOLET); canvas.rect(0, PAGE_H - 9, PAGE_W*0.4, 9, fill=1, stroke=0)
        try:
            img = ImageReader(LOGO); iw, ih = img.getSize()
            h = 8*mm; w = h * iw / ih
            canvas.drawImage(img, MX, PAGE_H - 24, width=w, height=h, mask="auto")
        except Exception:
            pass
        canvas.setFont("Helvetica-Bold", 8.5); canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - MX, PAGE_H - 20, "%02d-dars" % num)
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.6)
        canvas.line(MX, 16*mm, PAGE_W - MX, 16*mm)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
        canvas.drawString(MX, 12*mm, "Husan Suyunov · IT Shaharcha, Zomin tumani filiali")
        canvas.drawRightString(PAGE_W - MX, 12*mm, "Sahifa %d" % doc.page)
        canvas.restoreState()
    return hf


def make_cover(num, title_lines, subtitle):
    def cover(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(INDIGO_D); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(INDIGO); canvas.circle(PAGE_W*0.86, PAGE_H*0.82, 150, fill=1, stroke=0)
        canvas.setFillColor(VIOLET); canvas.circle(PAGE_W*0.12, PAGE_H*0.10, 120, fill=1, stroke=0)
        canvas.setFillColor(SKY); canvas.circle(PAGE_W*0.92, PAGE_H*0.18, 60, fill=1, stroke=0)
        # logo card
        card_w, card_h = 96*mm, 42*mm
        cx, cy = MX, PAGE_H - 56*mm
        canvas.setFillColor(colors.white); canvas.roundRect(cx, cy, card_w, card_h, 10, fill=1, stroke=0)
        try:
            img = ImageReader(LOGO); iw, ih = img.getSize()
            pad = 7*mm; mw, mh = card_w - 2*pad, card_h - 2*pad
            sc = min(mw/iw, mh/ih); w = iw*sc; h = ih*sc
            canvas.drawImage(img, cx + (card_w-w)/2, cy + (card_h-h)/2, width=w, height=h, mask="auto")
        except Exception:
            pass
        canvas.setFillColor(SKY); canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(MX, PAGE_H - 78*mm, "%02d - DARS" % num)
        canvas.setFillColor(colors.white)
        y = PAGE_H - 94*mm
        fs = 31 if max(len(t) for t in title_lines) <= 20 else 26
        canvas.setFont("Helvetica-Bold", fs)
        for line in title_lines:
            canvas.drawString(MX, y, line); y -= (fs + 7) * 0.42 * mm + 6*mm
        canvas.setFillColor(colors.HexColor("#C7D2FE")); canvas.setFont("Helvetica", 12)
        canvas.drawString(MX, y - 1*mm, subtitle)
        canvas.setStrokeColor(VIOLET); canvas.setLineWidth(3)
        canvas.line(MX, 52*mm, MX + 60*mm, 52*mm)
        canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(MX, 42*mm, "Tayyorladi:  Husan Suyunov")
        canvas.setFillColor(colors.HexColor("#A5B4FC")); canvas.setFont("Helvetica", 10.5)
        canvas.drawString(MX, 35*mm, "IT Shaharcha - Yoshlar Axborot Texnologiyalari Markazi")
        canvas.drawString(MX, 29*mm, "Zomin tumani filiali")
        canvas.drawString(MX, 21*mm, "Django · Python · IT Creative Academy")
        canvas.restoreState()
    return cover


def render(lesson):
    num = lesson["num"]
    out = os.path.join(ROOT, lesson["folder"], lesson["folder"] + " - Qollanma.pdf")
    doc = BaseDocTemplate(out, pagesize=A4, leftMargin=MX, rightMargin=MX,
                          topMargin=26*mm, bottomMargin=20*mm,
                          title="%02d-dars: %s" % (num, " ".join(lesson["title"])),
                          author="Husan Suyunov - IT Shaharcha Zomin")
    frame = Frame(MX, 20*mm, W, PAGE_H - 46*mm, id="main")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame],
                     onPage=make_cover(num, lesson["title"], lesson["subtitle"])),
        PageTemplate(id="body", frames=[frame], onPage=make_header_footer(num)),
    ])
    e = []; A = e.append
    A(NextPageTemplate("body")); A(PageBreak())

    sec = 0
    for blk in lesson["blocks"]:
        kind = blk[0]
        if kind == "badge":
            # avtomatik rang
            color = blk[2] if len(blk) > 2 else CYCLE[sec % len(CYCLE)]
            A(Badge(blk[1], color, W)); A(Spacer(1, 3)); sec += 1
            render._last = color
        elif kind == "p":
            A(Paragraph(blk[1], BODY))
        elif kind == "code":
            A(code_block(blk[1]))
        elif kind == "callout":
            color = blk[3] if len(blk) > 3 else getattr(render, "_last", INDIGO)
            A(callout(blk[1], blk[2], color))
        elif kind == "table":
            color = blk[2] if len(blk) > 2 else getattr(render, "_last", INDIGO)
            A(kv_table(blk[1], color))
        elif kind == "space":
            A(Spacer(1, blk[1]))
        elif kind == "pagebreak":
            A(PageBreak())
        elif kind == "sign":
            A(Spacer(1, 8)); A(HR(W, INDIGO, 1.2)); A(Spacer(1, 4))
            A(Paragraph(
                "<b>Tayyorladi:</b> Husan Suyunov<br/>"
                "IT Shaharcha &mdash; Yoshlar Axborot Texnologiyalari Markazi, "
                "Zomin tumani filiali",
                style("sg", fontName="Helvetica", fontSize=9.5, leading=14, textColor=SLATE)))
    doc.build(e)
    print("OK:", out)


# ====================================================================== LESSONS
LESSONS = [
{
 "num": 1, "folder": "01-dars django bilan tanishuv github bilan ishlash",
 "title": ["Django bilan tanishuv,", "GitHub bilan ishlash"],
 "subtitle": "venv · django-admin · runserver · git · GitHub",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Bu birinchi darsda biz <b>Django</b> bilan tanishamiz: u nima, "
         "qanday o'rnatiladi va birinchi loyihani qanday yaratamiz. So'ngra "
         "kodimizni <b>GitHub</b>ga joylashni o'rganamiz."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Django nima va u qanday ishlaydi;",
       "&bull;  Virtual muhit (venv) yaratish va faollashtirish;",
       "&bull;  Django loyihasini yaratish va serverni ishga tushirish;",
       "&bull;  Loyiha fayllari (settings, urls) vazifasi;",
       "&bull;  git va GitHub bilan kodni saqlash."]),
   ("space", 6),
   ("badge", "1. Django nima?"),
   ("p", "<b>Django</b> &mdash; Python tilida yozilgan, tez va xavfsiz veb-saytlar "
         "yaratish uchun mo'ljallangan freymvork (tayyor vositalar to'plami). "
         "U \"batareyalari bilan birga\" keladi: admin panel, ma'lumotlar bazasi "
         "(ORM), xavfsizlik va boshqalar tayyor holda beriladi."),
   ("badge", "2. Virtual muhit (venv) yaratish"),
   ("p", "Har bir loyiha uchun alohida muhit yaratish yaxshi amaliyot. Bu "
         "kutubxonalar bir-biriga xalaqit bermasligini ta'minlaydi."),
   ("code", [
       "# venv yaratish",
       "python -m venv venv",
       "",
       "# faollashtirish (Windows)",
       "venv\\Scripts\\activate",
       "",
       "# Django o'rnatish",
       "pip install django"]),
   ("badge", "3. Loyiha yaratish va ishga tushirish"),
   ("code", [
       "# config nomli loyiha yaratamiz (joriy papkada)",
       "django-admin startproject config .",
       "",
       "# serverni ishga tushiramiz",
       "python manage.py runserver",
       "",
       "# Brauzer:  http://127.0.0.1:8000/"]),
   ("pagebreak",),
   ("badge", "4. Loyiha tuzilishi"),
   ("table", [
       ("Fayl / papka", "Vazifasi"),
       ("manage.py", "Loyihani boshqarish buyruqlari (runserver, migrate...)."),
       ("config/settings.py", "Barcha sozlamalar: ilovalar, baza, til, vaqt."),
       ("config/urls.py", "Sayt manzillari (URL) jadvali."),
       ("config/wsgi.py", "Serverga ulanish (deploy uchun)."),
       ("config/asgi.py", "Asinxron server uchun ulanish."),
       ("db.sqlite3", "Standart ma'lumotlar bazasi fayli.")]),
   ("space", 8),
   ("badge", "5. GitHub bilan ishlash"),
   ("p", "Kodni saqlash va boshqalar bilan ulashish uchun <b>git</b> va "
         "<b>GitHub</b>dan foydalanamiz. Avval keraksiz fayllarni "
         "<font face='Courier'>.gitignore</font>ga yozamiz (venv, db.sqlite3)."),
   ("code", [
       "git init",
       "git add .",
       'git commit -m "Birinchi commit"',
       "git branch -M main",
       "git remote add origin https://github.com/foydalanuvchi/repo.git",
       "git push -u origin main"]),
   ("callout", "Eslatma:", [
       "&bull;  <b>.gitignore</b>ga <font face='Courier'>venv/</font> va "
       "<font face='Courier'>db.sqlite3</font> ni qo'shing;",
       "&bull;  parol/maxfiy kalitlarni hech qachon GitHubga yuklamang."], EMERALD),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  venv yarating va Django o'rnating;",
       "2.  'config' loyihasini yaratib, serverni ishga tushiring;",
       "3.  GitHubda repo oching va kodingizni push qiling."], ROSE),
   ("sign",),
 ],
},
{
 "num": 2, "folder": "02-dars Yangi app qo'shish hamda Hello world chiqarish",
 "title": ["Yangi app qo'shish va", "Hello World chiqarish"],
 "subtitle": "startapp · INSTALLED_APPS · View · urls · template",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Django loyihasi <b>app</b> (ilova)lardan tashkil topadi. Bu darsda "
         "yangi app yaratamiz, uni loyihaga ulaymiz va brauzerda birinchi "
         "<b>Hello World</b> sahifasini chiqaramiz."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Loyiha (project) va ilova (app) farqi;",
       "&bull;  Yangi app yaratish va ro'yxatga olish;",
       "&bull;  View (ko'rinish) yozish;",
       "&bull;  URL manzil ulash (include);",
       "&bull;  Template (HTML) ko'rsatish."]),
   ("space", 6),
   ("badge", "1. App yaratish"),
   ("p", "App &mdash; loyihaning mantiqiy bo'lagi (masalan: blog, do'kon, "
         "foydalanuvchilar). Yangi app yaratamiz:"),
   ("code", ["python manage.py startapp newapp"]),
   ("p", "So'ng uni <font face='Courier'>config/settings.py</font> ichidagi "
         "<b>INSTALLED_APPS</b> ro'yxatiga qo'shamiz:"),
   ("code", [
       "INSTALLED_APPS = [",
       "    # ...",
       "    'newapp',",
       "]"]),
   ("badge", "2. View yozish"),
   ("p", "View &mdash; so'rovni (request) qabul qilib, javob (sahifa) qaytaruvchi "
         "funksiya yoki klass. Biz klass asosidagi View yozamiz:"),
   ("code", [
       "from django.shortcuts import render",
       "from django.views import View",
       "",
       "class HelloWorldView(View):",
       "    def get(self, request):",
       "        return render(request, 'hello_world.html')"]),
   ("badge", "3. URL ulash"),
   ("p", "Avval app ichida <font face='Courier'>newapp/urls.py</font> yaratamiz:"),
   ("code", [
       "from .views import HelloWorldView",
       "from django.urls import path",
       "",
       "urlpatterns = [",
       "    path('', HelloWorldView.as_view(), name='hello_world'),",
       "]"]),
   ("p", "So'ng uni asosiy <font face='Courier'>config/urls.py</font>ga ulaymiz:"),
   ("code", [
       "from django.urls import path, include",
       "",
       "urlpatterns = [",
       "    path('admin/', admin.site.urls),",
       "    path('hello/', include('newapp.urls')),",
       "]"]),
   ("pagebreak",),
   ("badge", "4. Template (HTML) yaratish"),
   ("p", "App ichida <font face='Courier'>newapp/templates/hello_world.html</font> "
         "faylini yaratamiz:"),
   ("code", [
       "<!DOCTYPE html>",
       "<html>",
       "<head><title>Hello</title></head>",
       "<body>",
       "    <h1>Hello, World!</h1>",
       "    <p>This is a simple Django template.</p>",
       "</body>",
       "</html>"]),
   ("space", 6),
   ("badge", "5. Natijani ko'rish"),
   ("code", [
       "python manage.py runserver",
       "# Brauzer:  http://127.0.0.1:8000/hello/"]),
   ("callout", "Qanday ishlaydi?", [
       "&bull;  Brauzer /hello/ manzilini so'raydi;",
       "&bull;  config/urls.py uni newapp/urls.py ga yo'naltiradi;",
       "&bull;  View hello_world.html shablonini qaytaradi."], EMERALD),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  'newapp' app yarating va INSTALLED_APPS ga qo'shing;",
       "2.  HelloWorldView yozing va URL ulang;",
       "3.  o'z ism-familiyangizni chiqaruvchi HTML sahifa yarating."], ROSE),
   ("sign",),
 ],
},
{
 "num": 3, "folder": "03-dars Templates tayanch templates bilan ishlash",
 "title": ["Templates bilan", "ishlash (asoslar)"],
 "subtitle": "DIRS · extends · block · {% url %} · Bootstrap",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Bu darsda HTML shablonlar (templates) bilan chuqurroq ishlaymiz: "
         "umumiy <b>base.html</b> yaratib, undan boshqa sahifalarni meros "
         "olamiz va <b>Bootstrap</b> bilan chiroyli ko'rinish beramiz."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Umumiy templates papkasini sozlash;",
       "&bull;  base.html va meros olish (extends);",
       "&bull;  block teglari bilan kontent joylash;",
       "&bull;  {% url %} bilan havola yaratish;",
       "&bull;  Bootstrap navbar qo'shish."]),
   ("space", 6),
   ("badge", "1. templates papkasini sozlash"),
   ("p", "Loyiha ildizida umumiy <font face='Courier'>templates/</font> papka "
         "yaratamiz va <font face='Courier'>settings.py</font>da ko'rsatamiz:"),
   ("code", [
       "TEMPLATES = [",
       "    {",
       "        # ...",
       "        'DIRS': [BASE_DIR / 'templates'],",
       "        'APP_DIRS': True,",
       "    },",
       "]"]),
   ("badge", "2. base.html (asosiy shablon)"),
   ("p", "Barcha sahifalar uchun umumiy qism (navbar, css). "
         "<b>block</b> &mdash; o'zgaradigan joy:"),
   ("code", [
       "<!DOCTYPE html>",
       "<html>",
       "<head>",
       "  <link href='.../bootstrap.min.css' rel='stylesheet'>",
       "</head>",
       "<body>",
       "  <nav> ... navbar ... </nav>",
       "  {% block content %}{% endblock %}",
       "</body>",
       "</html>"]),
   ("badge", "3. Sahifa yasash (extends)"),
   ("p", "home.html base.html dan meros oladi va faqat o'z qismini yozadi:"),
   ("code", [
       "{% extends 'base.html' %}",
       "",
       "{% block content %}",
       "    <h1>Bu IT Creative ning Bosh saxifasi</h1>",
       "    <p>Saxifaga xush kelibsiz!</p>",
       "{% endblock %}"]),
   ("pagebreak",),
   ("badge", "4. View va URL'lar"),
   ("p", "Har bir sahifa uchun view va manzil:"),
   ("code", [
       "# views.py",
       "def home(request):",
       "    return render(request, 'home.html')",
       "",
       "def blog(request):",
       "    return render(request, 'blogs.html')",
       "",
       "# urls.py",
       "urlpatterns = [",
       "    path('', home, name='home'),",
       "    path('yangiliklar-saxifasi/', blog, name='blogs'),",
       "]"]),
   ("badge", "5. {% url %} bilan havola"),
   ("p", "Navbarda manzilni qattiq yozmasdan, nomi orqali bog'laymiz:"),
   ("code", [
       "<a href=\"{% url 'home' %}\">Bosh saxifa</a>",
       "<a href=\"{% url 'blogs' %}\">Blog</a>"]),
   ("callout", "Nega {% url %} yaxshi?", [
       "&bull;  Manzil o'zgarsa, faqat urls.py'ni tahrirlaysiz;",
       "&bull;  havolalar avtomatik to'g'ri qoladi."], SKY),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  base.html yarating va navbar qo'shing;",
       "2.  home va blog sahifalarini extends bilan yasang;",
       "3.  navbarda {% url %} orqali havolalarni ulang;",
       "4.  'Biz haqimizda' nomli yangi sahifa qo'shing."], ROSE),
   ("sign",),
 ],
},
{
 "num": 4, "folder": "04-dars Django models bilan ishlash User model yaratish",
 "title": ["Models bilan ishlash,", "User model yaratish"],
 "subtitle": "Model · ORM · ForeignKey · migrate · admin",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Bu darsda ma'lumotlar bazasi bilan ishlashni boshlaymiz. Django "
         "<b>model</b>lari yordamida Python klassi orqali jadval yaratamiz "
         "&mdash; bu <b>ORM</b> deyiladi (SQL yozmaymiz)."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Model nima va ORM qanday ishlaydi;",
       "&bull;  User va Blogs modellarini yozish;",
       "&bull;  ForeignKey bilan bog'lash;",
       "&bull;  makemigrations va migrate;",
       "&bull;  admin panel va createsuperuser."]),
   ("space", 6),
   ("badge", "1. Model yozish"),
   ("p", "<font face='Courier'>myapp/models.py</font>da ikki model yaratamiz. "
         "Har bir model &mdash; bazadagi bitta jadval, har bir maydon &mdash; ustun:"),
   ("code", [
       "from django.db import models",
       "",
       "class User(models.Model):",
       "    name = models.CharField(max_length=100)",
       "    surname = models.CharField(max_length=100)",
       "    age = models.IntegerField()",
       "",
       "    def __str__(self):",
       "        return f'{self.name} {self.surname}'",
       "",
       "class Blogs(models.Model):",
       "    title = models.CharField(max_length=200)",
       "    content = models.TextField()",
       "    author = models.ForeignKey(User, on_delete=models.CASCADE)",
       "",
       "    def __str__(self):",
       "        return self.title"]),
   ("badge", "2. ForeignKey nima?"),
   ("p", "<b>ForeignKey</b> bir modelni boshqasiga bog'laydi. Bu yerda har bir "
         "<b>Blogs</b> qaysidir <b>User</b>ga tegishli (bittadan-ko'pga aloqa). "
         "<font face='Courier'>on_delete=CASCADE</font> &mdash; user o'chsa, "
         "uning bloglari ham o'chadi."),
   ("badge", "3. Migration: bazaga o'tkazish"),
   ("code", [
       "python manage.py makemigrations",
       "python manage.py migrate"]),
   ("callout", "Ikkisining farqi:", [
       "&bull;  <b>makemigrations</b> &mdash; o'zgarishlardan 'reja' tuzadi;",
       "&bull;  <b>migrate</b> &mdash; rejani bazaga qo'llaydi (jadval yaratadi)."], EMERALD),
   ("pagebreak",),
   ("badge", "4. Admin panelga ulash"),
   ("p", "<font face='Courier'>myapp/admin.py</font>da modellarni ro'yxatdan "
         "o'tkazamiz:"),
   ("code", [
       "from django.contrib import admin",
       "from .models import User, Blogs",
       "",
       "admin.site.register(User)",
       "admin.site.register(Blogs)"]),
   ("p", "Admin foydalanuvchi yaratib, panelga kiramiz:"),
   ("code", [
       "python manage.py createsuperuser",
       "python manage.py runserver",
       "# Brauzer:  http://127.0.0.1:8000/admin/"]),
   ("space", 6),
   ("badge", "5. __str__ metodi"),
   ("p", "<b>__str__</b> obyekt admin panelda qanday nom bilan ko'rinishini "
         "belgilaydi. Usiz 'User object (1)' ko'rinadi, u bilan esa "
         "'Ali Valiyev' kabi tushunarli chiqadi."),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  User va Blogs modellarini yozing;",
       "2.  makemigrations va migrate ishga tushiring;",
       "3.  createsuperuser orqali admin yarating;",
       "4.  admin orqali 2 ta User va 3 ta Blog qo'shing."], ROSE),
   ("sign",),
 ],
},
{
 "num": 5, "folder": "05-dars ITC-Blogs Loyihasi. View hamda templates`lar bilan ishlash",
 "title": ["ITC-Blogs loyihasi:", "View va templates"],
 "subtitle": "objects.all() · context · {% for %} · ForeignKey",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Bu darsda bazadagi ma'lumotlarni saytda chiqaramiz. View orqali "
         "bloglarni olib, <b>context</b> bilan shablonga uzatamiz va "
         "<b>{% for %}</b> tsikli bilan ekranga chiqaramiz."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Modeldan ma'lumot olish (objects.all());",
       "&bull;  context orqali templatega uzatish;",
       "&bull;  {% for %} va {{ }} bilan ko'rsatish;",
       "&bull;  ForeignKey orqali bog'liq ma'lumotni chiqarish;",
       "&bull;  Bootstrap bilan bezash."]),
   ("space", 6),
   ("badge", "1. View'da ma'lumot olish"),
   ("p", "<font face='Courier'>blogapp/views.py</font>da barcha bloglarni olamiz "
         "va <b>context</b> (lug'at) orqali shablonga beramiz:"),
   ("code", [
       "from django.shortcuts import render",
       "from .models import Blogs",
       "",
       "def home(request):",
       "    blogs = Blogs.objects.all()",
       "    context = {",
       "        'blogs': blogs",
       "    }",
       "    return render(request, 'home.html', context)"]),
   ("badge", "2. URL ulash"),
   ("code", [
       "from .views import home",
       "from django.urls import path",
       "",
       "urlpatterns = [",
       "    path('', home, name='home'),",
       "]"]),
   ("badge", "3. Templatega ma'lumot chiqarish"),
   ("p", "<b>{% for %}</b> tsikli har bir blogni aylanib chiqadi. "
         "<b>{{ }}</b> ichida qiymatlarni ko'rsatamiz. "
         "Author &mdash; ForeignKey, shuning uchun "
         "<font face='Courier'>blog.author.name</font> deb murojaat qilamiz:"),
   ("code", [
       "{% for blog in blogs %}",
       "  <div class='row'>",
       "    <h2>{{ blog.title }}</h2>",
       "    <p>{{ blog.content }}</p>",
       "    <i>{{ blog.author.name }} {{ blog.author.surname }}</i>",
       "  </div>",
       "{% endfor %}"]),
   ("pagebreak",),
   ("badge", "4. Ma'lumot oqimi (qanday ishlaydi?)"),
   ("table", [
       ("Bosqich", "Nima sodir bo'ladi"),
       ("1. Request", "Foydalanuvchi '/' manzilini ochadi."),
       ("2. View", "home() funksiyasi ishga tushadi."),
       ("3. ORM", "Blogs.objects.all() bazadan bloglarni oladi."),
       ("4. Context", "Ma'lumot lug'at orqali shablonga uzatiladi."),
       ("5. Template", "{% for %} har bir blogni HTMLga chiqaradi."),
       ("6. Response", "Tayyor sahifa brauzerга qaytariladi.")]),
   ("space", 8),
   ("badge", "5. Bootstrap bilan bezash"),
   ("p", "home.html ichida Bootstrap CSS ulanadi va bloglar "
         "<font face='Courier'>container / row / col</font> ichida chiroyli "
         "joylashtiriladi. Bu mobil qurilmalarda ham yaxshi ko'rinadi."),
   ("callout", "Maslahat:", [
       "&bull;  Agar bloglar ko'rinmasa &mdash; avval admin orqali blog qo'shing;",
       "&bull;  author bo'sh bo'lsa, oldin User yarating."], SKY),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  home view'da barcha bloglarni oling;",
       "2.  context orqali templatega uzating;",
       "3.  {% for %} bilan bloglarni chiqaring;",
       "4.  har bir blog muallifini (author) ko'rsating."], ROSE),
   ("sign",),
 ],
},
{
 "num": 6, "folder": "06-dars Database chizmalari",
 "title": ["Database chizmalari", "(modelni loyihalash)"],
 "subtitle": "ER-diagramma · field turlari · News modeli · migrate",
 "blocks": [
   ("badge", "Dars haqida", VIOLET),
   ("p", "Loyihani kod yozishdan oldin <b>ma'lumotlar bazasi chizmasi</b> "
         "(database design) tuzish kerak. Bu darsda News (yangilik) modelini "
         "loyihalaymiz va kerakli field (maydon) turlarini tanlaymiz."),
   ("callout", "Dars yakunida siz quyidagilarni bilasiz:", [
       "&bull;  Database chizmasi nima va nega kerak;",
       "&bull;  Asosiy field turlarini tanlash;",
       "&bull;  News modelini yozish;",
       "&bull;  FileField va default qiymatlar;",
       "&bull;  migration bilan jadval yaratish."]),
   ("space", 6),
   ("badge", "1. Database chizmasi nima?"),
   ("p", "Database chizmasi &mdash; qaysi jadvallar, ularda qanday ustunlar va "
         "qanday bog'lanishlar bo'lishini oldindan rejalashtirishdir. To'g'ri "
         "chizma keyinchalik ko'p xatolardan saqlaydi."),
   ("badge", "2. Field (maydon) turlari"),
   ("table", [
       ("Field turi", "Vazifasi"),
       ("CharField", "Qisqa matn (sarlavha). max_length majburiy."),
       ("TextField", "Uzun matn (maqola tanasi)."),
       ("IntegerField", "Butun son (likes, views, comments)."),
       ("FileField", "Fayl yuklash (rasm, hujjat)."),
       ("BooleanField", "Ha/yo'q (True/False) qiymat."),
       ("DateTimeField", "Sana va vaqt.")]),
   ("space", 8),
   ("badge", "3. News modelini yozish"),
   ("p", "<font face='Courier'>news/models.py</font>da yangilik modelini "
         "yaratamiz. <font face='Courier'>default=0</font> &mdash; boshlang'ich "
         "qiymat, <font face='Courier'>blank/null=True</font> &mdash; "
         "maydon bo'sh bo'lishi mumkin:"),
   ("code", [
       "from django.db import models",
       "",
       "class News(models.Model):",
       "    title = models.CharField(max_length=200)",
       "    content = models.TextField()",
       "    file = models.FileField(upload_to='news_file/',",
       "        blank=True, null=True)",
       "    likes = models.IntegerField(default=0)",
       "    comments = models.IntegerField(default=0)",
       "    views = models.IntegerField(default=0)",
       "    tags = models.CharField(max_length=100,",
       "        blank=True, null=True)",
       "",
       "    def __str__(self):",
       "        return self.title"]),
   ("pagebreak",),
   ("badge", "4. Bazaga o'tkazish"),
   ("code", [
       "python manage.py makemigrations",
       "python manage.py migrate"]),
   ("p", "<font face='Courier'>FileField</font> ishlashi uchun "
         "<b>Pillow</b> kutubxonasi kerak bo'lishi mumkin:"),
   ("code", ["pip install Pillow"]),
   ("space", 6),
   ("badge", "5. Admin orqali tekshirish"),
   ("p", "Modelni admin panelga ulab, yangilik qo'shib ko'ramiz:"),
   ("code", [
       "from django.contrib import admin",
       "from .models import News",
       "",
       "admin.site.register(News)"]),
   ("callout", "Keyingi dars bilan bog'liqlik:", [
       "&bull;  Bu darsda yassi (flat) model tuzdik;",
       "&bull;  07-darsda uni Category/News/Comment'ga bo'lib, "
       "ForeignKey bilan bog'laymiz."], SKY),
   ("space", 8),
   ("badge", "Amaliy topshiriq", ROSE),
   ("callout", "Mustaqil bajaring:", [
       "1.  News modelini yozing;",
       "2.  makemigrations va migrate qiling;",
       "3.  admin orqali 3 ta yangilik qo'shing;",
       "4.  Qo'shimcha: 'is_active' (BooleanField) maydonini qo'shing."], ROSE),
   ("sign",),
 ],
},
]


if __name__ == "__main__":
    for L in LESSONS:
        render(L)
    print("Barchasi tayyor.")
