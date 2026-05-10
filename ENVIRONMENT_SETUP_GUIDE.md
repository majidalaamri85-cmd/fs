# 🔑 دليل إضافة متغيرات البيئة على Render

## المتغيرات المطلوبة

سيكون عليك إضافة المتغيرات التالية في Render Dashboard:

### ✅ المتطلب الأساسي

| اسم المتغير | القيمة | الملاحظات |
|-------------|--------|----------|
| `DEBUG` | `False` | ⚠️ مهم جداً للإنتاج |
| `PYTHON_VERSION` | `3.11.0` | إصدار Python |
| `SECRET_KEY` | (يتم إنشاؤه) | يجب أن يكون موجوداً |

---

## 🔧 خطوات الإضافة (الطريقة 1: من الويب)

### الخطوة 1: دخول Dashboard
```
1. اذهب إلى: https://dashboard.render.com
2. سجّل الدخول بحسابك
3. اختر الخدمة: food-safety-system (أو fs-taxn)
```

### الخطوة 2: فتح قسم البيئة
```
1. من صفحة الخدمة، ابحث عن تبويب "Environment"
2. يجب أن يكون في الشريط العلوي للصفحة
3. انقر عليه لفتح قائمة المتغيرات
```

### الخطوة 3: إضافة المتغيرات
```
أ) انقر على "Add Environment Variable"

ب) أضف DEBUG:
   - Key: DEBUG
   - Value: False
   - اضغط: Add

ج) أضف PYTHON_VERSION:
   - Key: PYTHON_VERSION
   - Value: 3.11.0
   - اضغط: Add

د) تحقق من SECRET_KEY:
   - يجب أن يكون موجود بالفعل
   - إذا لم يكن، اطلب من Render إنشاؤه (generateValue: true)
```

### الخطوة 4: الحفظ والنشر
```
1. انقر "Save" أو "Update Environment"
2. انتظر رسالة التأكيد
3. الخدمة ستُعاد تشغيلها تلقائيًا
```

---

## 📝 متغيرات اختيارية (اذا كنت تريد الصور)

إذا كنت تريد استخدام Cloudinary لتخزين الصور:

```
CLOUDINARY_CLOUD_NAME = your-cloud-name
CLOUDINARY_API_KEY = your-api-key
CLOUDINARY_API_SECRET = your-api-secret
```

للحصول عليها:
1. اذهب إلى https://cloudinary.com
2. إنشئ حساب مجاني
3. انسخ بيانات من Dashboard → Account

---

## ⚙️ خطوات إعادة النشر (بعد إضافة المتغيرات)

```
1. من Render Dashboard
2. اذهب إلى صفحة الخدمة
3. انقر "Deploy latest commit"
4. أو انقر "Clear build cache" ثم "Deploy"
5. انتظر انتهاء البناء
```

---

## ✅ كيفية التحقق من النجاح

بعد النشر مباشرة:

1. اذهب إلى: https://fs-taxn.onrender.com
2. إذا رأيت:
   - ✅ صفحة الموقع تحمل بدون خطأ 500
   - ✅ جدول البيانات موجود
   - ✅ لا توجد رسائل خطأ

فهذا يعني أن المتغيرات تعمل بشكل صحيح!

---

## 🆘 استكشاف الأخطاء

### مشكلة: لا تزال ترى خطأ 500
```
الحل:
1. افتح Render Dashboard
2. انقر على "Logs"
3. ابحث عن رسالة الخطأ
4. إذا كانت عن DEBUG:
   - تأكد من أن DEBUG = False
5. إذا كانت عن PYTHON_VERSION:
   - تأكد من أن قيمتها = 3.11.0
```

### مشكلة: قاعدة البيانات فارغة
```
الحل: هذا طبيعي! الأمر build.sh سيملأها:
- python manage.py migrate
- python manage.py seed_governorates
- python manage.py seed_items
```

### مشكلة: لا أرى قسم Environment
```
الحل:
1. تأكد أنك تشاهد الخدمة الصحيحة
2. يجب أن تكون من نوع "Web Service"
3. اضغط على أيقونة الإعدادات (Settings)
4. ثم ابحث عن Environment
```

---

## 📋 نموذج سريع للنسخ

```
DEBUG=False
PYTHON_VERSION=3.11.0
```

---

## 🎯 الخطوة الأخيرة

بعد إضافة المتغيرات والنشر:

```bash
# اختبر الموقع مباشرة
https://fs-taxn.onrender.com

# يجب أن ترى:
# ✅ صفحة الموقع الرئيسية بدون أخطاء
# ✅ القوائم تعمل
# ✅ البيانات تظهر
```

---

**ملاحظة مهمة:** إذا كان لديك أي سؤال، اقرأ ملف [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) للشرح الكامل.

*آخر تحديث: 7 مايو 2026*
