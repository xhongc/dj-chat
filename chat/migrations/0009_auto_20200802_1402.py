# Generated by Django 2.2.14 on 2020-08-02 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_history_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='img_path',
            field=models.CharField(default='https://s1.ax1x.com/2020/07/23/ULRdD1.png', help_text='头像地址', max_length=255),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='img_path',
            field=models.CharField(default='https://s1.ax1x.com/2020/07/23/ULgnPg.png', help_text='头像地址', max_length=255),
        ),
    ]
