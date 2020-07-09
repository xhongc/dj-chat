function getFriends() {
    $.get('/api/friends/').success(function (data) {
        $('#id_friends_list').empty();
        $.each(data, function (k, v) {
            var html = '<li class="list-group-item" channel_no="%s">\n' +
                '                                    <div>\n' +
                '                                        <figure class="avatar">\n' +
                '                                            <img src="%s" class="rounded-circle">\n' +
                '                                        </figure>\n' +
                '                                    </div>\n' +
                '                                    <div class="users-list-body">\n' +
                '                                        <h5>%s</h5>\n' +
                '                                        <p>%s</p>\n' +
                '              <div class="users-list-action">\n' +
                '                  <span class="badge badge-danger" id="id_badge_ntf">%s</span>\n' +
                '              </div>\n' +
                '                                    </div>\n' +
                '                                </li>';
            html = html.format(v.unicode_id, v.img_path, v.nick_name, v.signature, v.unread_no);
            $('#id_friends_list').append(html)
        })
    })
}

function getChatRoome() {
    $('#id_chats').empty();
    $.get('/api/chat_room/').success(function (data) {
        $.each(data, function (k, v) {
            var html = '<li class="list-group-item" channel_no="%s" id="%s">\n' +
                '          <div>\n' +
                '              <figure class="avatar">\n' +
                '                  <img src="%s" class="rounded-circle">\n' +
                '              </figure>\n' +
                '          </div>\n' +
                '          <div class="users-list-body">\n' +
                '              <h5>%s</h5>\n' +
                '              <p>%s</p>\n' +
                '              <div class="users-list-action">\n' +
                '                  <span class="badge badge-danger" id="id_badge_ntf">%s</span>\n' +
                '              </div>\n' +
                '          </div>\n' +
                '      </li>';
            html = html.format(v.channel_no, v.channel_no, v.img_path, v.room_name, v.room_description, v.unread_no);
            $('#id_chats').append(html)
        })
    })
}

function postFriend() {
    let uid = $('#id_friend_uid').val();
    $.ajax({
        url: '/api/friends/',
        type: 'post',
        data: {'uid': uid},
        success: function () {
            xtip.msg('添加成功')
        },
        error: function (data) {
            xtip.msg(data.responseText)
        }
    })
}

function getChatRoomInfo(channel_no) {
    $.get('/api/chat_room/', {'channel_no': channel_no}).success(function (data) {
        $('.id_room_name').html(data[0].room_name);
        $('.id_room_description').html(data[0].room_description);
        $('.id_room_img').attr('src', data[0].img_path);
        $('.id_channel_no').html(channel_no);
        var max_number = data[0].max_number;
        var members_list = data[0]['members'];
        var admin_list = data[0]['admins'];
        $('#id_group').attr('channel_no', channel_no);
        $('#id_member_count').html('群成员(%s/%s)'.format(members_list.length, max_number));
        $('#id_admin_name').html(admin_list[0].nick_name);
        $('#id_admin_signature').html(admin_list[0].signature);
        $('#id_admin_img_path').attr('src', admin_list[0].img_path);
        $('#id_member_list').empty();
        if (members_list) {
            $.each(members_list, function (k, v) {
                $('#id_member_list').append('<li class=\"list-group-item\">\n' +
                    '                <div>\n' +
                    '                  <figure class=\"avatar\">\n' +
                    '                    <img src=\"' + members_list[k].img_path + '\"' + 'class=\"rounded-circle\">\n' +
                    '                  </figure>\n' +
                    '                </div>\n' +
                    '                <div class=\"users-list-body\">\n' +
                    '                  <h5>' + members_list[k].nick_name + '</h5>\n' +
                    '                  <p>' + members_list[k].signature + '</p>\n' +
                    '                </div>\n' +
                    '              </li>')
            });
        }

    })
}

function getChatLog(channel_no) {
    $.get('/api/chat_log/', {'said_to_room__channel_no': channel_no}).success(function (data) {
        data = data.results;
        var me = window.localStorage.user_id;
        if (data.length !== 0) {
            console.log('data');
            $.each(data, function (i, item) {
                if (item.who_said === parseInt(me)) {
                    ChatosExamle.Message.add(item.content, 'inside-message', item.chat_datetime);
                } else {
                    ChatosExamle.Message.add(item.content, 'outgoing-message', item.chat_datetime);
                }
            });
            ChatosExamle.Info.add('---历史记录---', '', '');
        }
    })
}

function getPersonalChatLog(channel_no) {
    $.get('/api/personal_chat_log/', {'who_said__profile__unicode_id': channel_no}).success(function (data) {
        data = data.results;
        var me = window.localStorage.user_id;
        if (data.length !== 0) {
            console.log('data');
            $.each(data, function (i, item) {
                if (item.who_said === parseInt(me)) {
                    ChatosExamle.Message.add(item.content, 'inside-message', item.chat_datetime);
                } else {
                    ChatosExamle.Message.add(item.content, 'outgoing-message', item.chat_datetime);
                }
            });
            ChatosExamle.Info.add('---历史记录---', '', '');
        }
    })
}
