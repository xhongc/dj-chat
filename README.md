# Django Websocket 聊天系统
## 技术栈
<br>
django-channels + bootstrap + jquery 

## 安装
1. pip install -r requirement.txt
2. [安装运行redis](https://www.runoob.com/redis/redis-install.html)
3. python manage.py migrate #初始化数据库
4. python manage.py createsuperuser #创建管理员账户
4. `python manage.py runserver 8088` or 
`daphne -b 127.0.0.1 -p 8088 dj_chat.asgi:application`
5. 访问127.0.0.1:8088 
## 界面截图
![](https://s1.ax1x.com/2020/07/11/Ul8LZ9.png)
![](https://s1.ax1x.com/2020/07/11/UlYYKU.png)

## 后续开发计划
- [ ]  用户注册
- [ ]  说说功能
- [ ]  搜索/添加 好友/群组界面优化

