FROM nginx

#对外暴露端口
EXPOSE 80

RUN mkdir -p /home/ubuntu/chat_log
RUN rm /etc/nginx/conf.d/default.conf
ADD ./nginx/nginx-chat.conf  /etc/nginx/conf.d/
ADD ./templates/chat/boot_chat.html  /home/ubuntu/
