# دليل نشر المشروع على Render

## ✅ الملفات المُعدّة للنشر

- ✅ `render.yaml` - ملف إعدادات Render
- ✅ `runtime.txt` - إصدار Python (3.11.0)
- ✅ `build.sh` - سكريبت البناء والهجرة
- ✅ `requirements.txt` - المتطلبات
- ✅ `settings.py` - إعدادات Django للإنتاج

---

## 📋 خطوات النشر على Render

### الخطوة 1: تحضير مستودع GitHub

```bash
# تأكد من أن جميع التغييرات مُحفوظة
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### الخطوة 2: إنشاء خدمة جديدة على Render

1. انتقل إلى [https://render.com](https://render.com)
2. سجّل الدخول أو أنشئ حسابًا جديدًا
3. انقر على **New +** → **Web Service**
4. اختر **Connect a repository**
5. اختر مستودع المشروع من GitHub
6. اتبع الخطوات التالية:

### الخطوة 3: إعدادات الخدمة

| الإعداد | القيمة |
|-------|--------|
| **Name** | `food-safety-system` (أو اسم آخر) |
| **Environment** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn food_safety_system.wsgi:application` |
| **Plan** | Free (أو أعلى حسب احتياجك) |

### الخطوة 4: متغيرات البيئة المطلوبة

أضف المتغيرات التالية في قسم **Environment Variables**:

```
SECRET_KEY          → سيتم إنشاؤه تلقائيًا بواسطة render.yaml
DEBUG               → False
PYTHON_VERSION      → 3.11.0
```

#### اختياري - Cloudinary (لتخزين الصور/الملفات)

إذا كنت تريد استخدام Cloudinary لتخزين الملفات:

1. انشئ حسابًا مجانيًا على [https://cloudinary.com](https://cloudinary.com)
2. أضف المتغيرات التالية:

```
CLOUDINARY_CLOUD_NAME    → من Cloudinary Dashboard
CLOUDINARY_API_KEY       → من Cloudinary API
CLOUDINARY_API_SECRET    → من Cloudinary API
```

### الخطوة 5: إعدادات قاعدة البيانات

**الخيار 1: استخدام SQLite (مجاني)**
- لا توجد إعدادات إضافية مطلوبة
- سيتم استخدام `db.sqlite3` تلقائيًا

**الخيار 2: استخدام PostgreSQL (موصى به)**
1. أضف **Postgres** من قسم **Attach Database**
2. سيتم تعيين `DATABASE_URL` تلقائيًا

### الخطوة 6: المراقبة والاختبار

بعد النشر:

```bash
# استعرض السجلات
Render Dashboard → Logs

# اختبر الموقع
https://<your-app-name>.onrender.com
```

---

## 🔒 نصائح الأمان

1. **لا تشارك SECRET_KEY** - يتم إنشاؤها تلقائيًا بواسطة Render
2. **استخدم HTTPS فقط** - يتم فرضه تلقائيًا على Render
3. **احم بيانات Cloudinary** - لا تشاركها مطلقًا
4. **راقب السجلات** للأخطاء والمشاكل

---

## 🛠️ استكشاف الأخطاء

### المشكلة: فشل البناء

```
❌ Check:
- أن جميع المتطلبات موجودة في requirements.txt
- أن build.sh قابل للتنفيذ
- سجلات البناء في Render Dashboard
```

### المشكلة: خطأ قاعدة البيانات

```
❌ Check:
- أن DATABASE_URL مُعيّن بشكل صحيح
- أن الهجرة تمت بنجاح (شاهد السجلات)
- أن PostgreSQL متصل (إن لزم الأمر)
```

### المشكلة: أخطاء CSRF

```
✅ Fix:
- تحقق من RENDER_EXTERNAL_HOSTNAME
- أعد تشغيل الخدمة
- امسح ذاكرة التخزين المؤقت
```

---

## 📊 المتطلبات المثبتة

```
Django>=5.0          - إطار العمل الرئيسي
gunicorn>=21.2       - خادم الويب
whitenoise>=6.6      - خدمة الملفات الثابتة
dj-database-url      - إدارة DATABASE_URL
psycopg2-binary      - دعم PostgreSQL
cloudinary           - تخزين الصور
django-cloudinary-storage - تكامل Cloudinary مع Django
```

---

## 🚀 بعد النشر الناجح

1. **تحديث DNS** - أشر نطاقك إلى Render (اختياري)
2. **تفعيل HTTPS** - يتم تلقائيًا
3. **المراقبة المستمرة** - شاهد السجلات بانتظام
4. **النسخ الاحتياطية** - قم بنسخ قاعدة البيانات بانتظام

---

## 📞 ملاحظات مهمة

- المتغيرات الحساسة محفوظة آمنة على Render
- الخدمة ستنام بعد 15 دقيقة من عدم النشاط (على الخطة المجانية)
- استخدم PostgreSQL للأداء والموثوقية الأفضل

---

**آخر تحديث:** 7 مايو 2026
**الإصدار:** 11 كامل (Complete)
