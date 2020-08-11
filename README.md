# Django Websocket 聊天系统
## 技术栈
<br>
django-channels + bootstrap + jquery 

项目地址参考：http://106.55.162.109:8888/ 账号：admin 密码：xhongc
## 界面截图
![](https://s1.ax1x.com/2020/07/28/aVKVhD.png)
![](https://s1.ax1x.com/2020/07/11/Ul8LZ9.png)
![](https://s1.ax1x.com/2020/07/11/UlYYKU.png)
## 安装
1. pip install -r requirement.txt
2. [安装运行redis](https://www.runoob.com/redis/redis-install.html)
3. python manage.py migrate #初始化数据库
4. python manage.py createsuperuser #创建管理员账户
4. `python manage.py runserver 8088` or 
`daphne -b 127.0.0.1 -p 8088 dj_chat.asgi:application`
5. 访问127.0.0.1:8088 

## 部署
> nginx + daphne + gunicorn + supervisor
- gunicorn，green unicorn 简称，unix系统的wsgi http服务器
处理符合wsgi的接口，使得底层处理与上层业务分开，Django仅负责业务层的处理，这里使用主要是官方推荐，uwsgi服务器使用的人也比较多
- daphne 支持HTTP, HTTP2 和 WebSocket 的asgi的服务器，这里主要是处理WebSocket 的请求
- supervisor 进程管理器，当web项目存在多个进程需要处理时，方便统一管理，如服务器down机重启时自启动等
- nginx 静态资源处理和请求的分发等，http请求指向gunicorn进程，websocket请求指向daphne进程等
> tips: gunicorn 和 daphne 开不同的端口[！](https://github.com/xhongc/dj-chat/blob/master/supervisor.conf)
#### nginx 配置
```nginx
server {
        listen 80;
        server_name 106.55.162.109;
        charset utf-8;
        client_max_body_size 75M;
        location /static {
            alias /home/ubuntu/dj-chat/static;
        }
        access_log /home/ubuntu/chat_log/access.log;
        error_log /home/ubuntu/chat_log/error.log;
        location / {
            proxy_pass http://127.0.0.1:8000;
            include /etc/nginx/uwsgi_params;
        }
        location /ws {
            proxy_pass http://127.0.0.1:8001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
            proxy_read_timeout  36000s;
            proxy_send_timeout  36000s;
        }
        root /var/www/html;
        index boot_chat.html;
}

```
## Docker 部署
```shell
docker-compose build
docker-compose up -d
```
详细流程跳转到[Docker部署应用 Django+daphne+Gunicorn+Nginx+Redis](https://xhongc.github.io/docker-django-daphne-gunicorn-nginx.html)
## 后续开发计划
- [ ] 开发音乐机器人（多人同步听歌）
8. 玩家在线离线头像变灰
9. 重新定义消息返回结构
- [ ] 开发视频机器人（多人视频）
- [ ] vue 重构前端

