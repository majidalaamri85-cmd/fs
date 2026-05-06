تشغيل النظام:

1) افتح التيرمنال داخل هذا المجلد:
food_safety_system_v11_complete

2) ثبّت المتطلبات:
pip install -r requirements.txt

3) نفّذ الهجرات:
python manage.py makemigrations
python manage.py migrate

4) أدخل البنود الـ100 تلقائياً:
python manage.py seed_items

5) شغل السيرفر:
python manage.py runserver

6) افتح الرابط:
http://127.0.0.1:8000/

ملاحظات:
- اسم مشروع Django هو: food_safety_system
- اسم التطبيق هو: inspections
- يدعم: إدخال التقييم، فتح/إغلاق الأقسام، مستوفي/غير مستوفي/لا ينطبق، صور متعددة، حساب النتيجة، تعديل، حذف، وتقرير Word.
