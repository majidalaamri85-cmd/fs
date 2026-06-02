from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0015_evaluation_eval_created_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تاريخ آخر تعديل'),
        ),
    ]
