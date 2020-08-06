// 获取好友列表
function getFriends() {
    $('.talks').hide();
    $('.homebox').hide();
    $.get('/api/friends/').success(function (data) {
        $('#id_friends_list').empty();
        $.each(data, function (k, v) {
            var html = '<li class="list-group-item" channel_no="%s" profile_id="%s">\n' +
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
            html = html.format(v.unicode_id, v.id, v.img_path, v.nick_name, v.signature, v.unread_no);
            $('#id_friends_list').append(html)
        })
    })
}

function getChatRoome() {
    $('#id_chats').empty();
    $('.talks').hide();
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

function getTalkLog() {
    $('#id_talks').empty();
    $('#id_talk_log').empty();
    $('.chatbox').hide();
    $('.homebox').hide();

    $.get('/api/talk_log').success(function (data) {
        $.each(data, function (k, v) {
            var html = '<li class="list-group-item">\n' +
                '              <div>\n' +
                '                <figure class="avatar">\n' +
                '                  <img src="%s" class="rounded-circle">\n' +
                '                </figure>\n' +
                '              </div>\n' +
                '              <div class="users-list-body">\n' +
                '                <h5>%s</h5>\n' +
                '                <p>%s</p>\n' +
                '                <div class="users-list-action action-toggle">\n' +
                '                  <div class="dropdown">\n' +
                '                    <a data-toggle="dropdown" href="http://www.jq22.com/demo/jqueryweblt201908272313/#">\n' +
                '                      <i class="ti-more"></i>\n' +
                '                    </a>\n' +
                '                    <div class="dropdown-menu dropdown-menu-right">\n' +
                '                      <a href="#" class="dropdown-item">Open</a>\n' +
                '                      <a href="#"\n' +
                '                         data-navigation-target="contact-information" class="dropdown-item">Profile</a>\n' +
                '                      <a href="#" class="dropdown-item">Add to\n' +
                '                        archive</a>\n' +
                '                      <a href="#" class="dropdown-item">Delete</a>\n' +
                '                    </div>\n' +
                '                  </div>\n' +
                '                </div>\n' +
                '              </div>\n' +
                '            </li>';
            html = html.format(v.profile.img_path, v.profile.nick_name, v.content.slice(0, 30));
            var talk_log_html = '<div class="ticketBox" >\n' +
                '            <div class="row">\n' +
                '              <div class="col-xs-3">\n' +
                '                <img src="%s" class="rounded-circle">\n' +
                '              </div>\n' +
                '              <div class="col-xs-6">\n' +
                '                <div class="ticket-name">\n' +
                '                  %s\n' +
                '                  <span>%s</span>\n' +
                '                </div>\n' +
                '                <span>点赞数: %s 阅读量: %s</span>\n' +
                '              </div>\n' +
                '\n' +
                '            </div>\n' +
                '            <div class="ticket-description">\n' +
                '              <p>%s<br>\n' +
                '              </p>\n' +
                '            </div>\n' +
                '          </div>'
            talk_log_html = talk_log_html.format(v.profile.img_path, v.profile.nick_name, v.profile.signature, v.star, v.reading, v.content);
            $('#id_talks').append(html);
            $('#id_talk_log').append(talk_log_html)

        })
    })
}

// 搜索群组
function getAllChatRoome() {
    $('#id_all_chat_romm').empty();
    $.get('/api/chat_room/?is_all=true').success(function (data) {
        if (data.length === 0) {
            $('#id_all_chat_romm').append('<p>暂无群组</p>')
        }
        $.each(data, function (k, v) {
            var html = '<li class="list-group-item" channel_no="%s" id="%s">\n' +
                '            <div style="float:left">\n' +
                '              <figure class="avatar">\n' +
                '                <img src="%s" class="rounded-circle">\n' +
                '              </figure>\n' +
                '            </div>\n' +
                '            <div class="ml-lg-3" style="float:left">\n' +
                '              <h5>%s</h5>\n' +
                '              <p>%s</p>\n' +
                '            </div>\n' +
                '            <div class="users-list-action" style="float:right">\n' +
                '                <button type="button" class="btn btn-success btn-pulse btn-floating" onClick="joinChatroom(\'%s\')"\n' +
                '                        id="id_test"><i class="ti-plus"></i></button>\n' +
                '              </div>\n' +
                '          </li>';
            html = html.format(v.channel_no, v.channel_no, v.img_path, v.room_name, v.room_description, v.channel_no);
            $('#id_all_chat_romm').append(html)
        })
    })
}

//搜索添加好友
function getFriendList() {
    $('#id_friend_list').empty();
    $.get('/api/user_profile/').success(function (data) {
        if (data.length === 0) {
            $('#id_friend_list').append('<p>暂无好友</p>')
        }
        $.each(data, function (k, v) {
            var html = `
            <li class="list-group-item" channel_no="${v.unicode_id}" id="${v.unicode_id}">
              <div style="float:left">
                <figure class="avatar">
                  <img src="${v.img_path}" class="rounded-circle">
                </figure>
              </div>
              <div class="ml-lg-3" style="float:left">
                <h5>${v.nick_name}</h5>
                <p>${v.signature}</p>
              </div>
              <div class="users-list-action" style="float:right">
                <button type="button" class="btn btn-success btn-pulse btn-floating" onClick="postUidFriend(${v.unicode_id})">
                  <i class="ti-plus"></i></button>
              </div>
            </li>
            `
            $('#id_friend_list').append(html)
        })
    })
}

function postUidFriend(uid) {
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

function postFriend() {
    var uid = $('#id_friend_uid').val();
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
    //todo
    // ChatosExamle.Info.add('<div id="player1"></div><hr>', '', '');
    $('#id_group').children().html('<div id="player1"></div><hr>')
    const ap = new APlayer({
        container: document.getElementById('player1'),
        mini: false,
        autoplay: false,
        theme: '#FADFA3',
        loop: 'all',
        order: 'random',
        preload: 'auto',
        volume: 0.7,
        mutex: true,
        listFolded: false,
        listMaxHeight: 90,
        lrcType: 1,
        audio: [
            {
                name: '霓虹甜心',
                artist: '马赛克乐队',
                url: 'http://m10.music.126.net/20200806212436/8ee9143d8089b398c7878aa79a474961/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a',
                cover: 'cover1.jpg',
                lrc: '[00:00.000] 作曲 : 夏颖/卓越\n[00:01.000] 作词 : 夏颖/卓越\n[00:07.947]霓虹甜心 - 马赛克乐队\n[00:12.700]词：夏颖&卓越\n[00:16.204]曲：夏颖&卓越\n[00:17.817]编曲：卓越\n[00:34.566]制作&混音：Wouter Vlaeminck\n[00:39.825]今夜我用尽所有的方式\n[00:43.576]才得到你的名字\n[00:48.071]此刻芳心要怎样才不流失\n[00:52.075]在这多彩的舞池\n[00:56.068]霓虹下你的影子那么美\n[01:00.072]我感觉我的心在动\n[01:04.574]你慢慢靠近耳边说了句 baby\n[01:08.321]我闻到你的香味\n[01:12.573]darling 你快来救救我\n[01:16.576]darling darling save me\n[01:20.328]darling 进入了音乐里\n[01:40.327]沉醉在这样的夜里\n[01:44.570]你是注定派给我的天使\n[01:48.826]抚慰我不安的种子\n[01:53.070]让这枯萎的生活重发新枝\n[01:57.073]爱是最美的情诗\n[02:00.825]霓虹下你的影子那么美\n[02:05.071]我感觉我的心在动\n[02:09.324]你慢慢靠近耳边说了句 baby\n[02:13.327]我闻到你的香味\n[02:17.322]daring 你快来救救我\n[02:20.572]darling darling save me\n[02:24.825]darling 进入了音乐里\n[02:29.071]沉醉在这样的夜里\n[02:33.324]darling 你快来救救我\n[02:37.329]darling darling save me\n[02:42.076]darling 进入了音乐里\n[02:46.580]沉醉在这样的夜里\n[02:49.821]就在转身的一瞬间\n[02:53.825]你性感的占领我世界\n[02:58.330]心跳已融化在音乐\n[03:02.323]告诉你我的感觉\n[03:09.077]daring 你快来救救我\n[03:12.076]darling darling save me\n[03:16.823]darling 进入了音乐里\n[03:20.827]沉醉在这样的夜里\n[03:26.077]darling 你快来救救我\n[03:29.074]darling darling save me\n[03:33.576]darling 进入了音乐里\n[03:36.828]沉醉在这样的夜里\n[03:39.078]沉醉在这样的夜里\n[03:43.822]沉醉在这样的夜里\n',
                theme: '#ebd0c2'
            },
            {
                name: 'name2',
                artist: 'artist2',
                url: 'http://m10.music.126.net/20200806212436/8ee9143d8089b398c7878aa79a474961/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a',
                cover: 'cover2.jpg',
                lrc: 'lrc2.lrc',
                theme: '#46718b'
            }
        ]
    });
    ap.play()
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

function getUserInfo(profile_id) {
    $.get('/api/user_info/%s/'.format(profile_id)).success(function (data) {
        $('.id_room_name').html(data.nick_name);
        $('.id_room_description').html(data.signature);
        $('.id_room_img').attr('src', data.img_path);
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
            ChatosExamle.Info.add('<div>历史记录</div><hr>', '', '');
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
            ChatosExamle.Info.add('<div>历史记录</div><hr>', '', '');
        }
    })
}

// 邀请好友进群
function investFriendsToRoom(channel_no, my_friends_list) {
    $.ajax({
        url: '/api/chat_room/%s/?channel_no=%s'.format(channel_no, channel_no),
        type: 'PUT',
        data: {'members': JSON.stringify(my_friends_list)},
        success: function (response) {
            xtip.msg('邀请成功');
            $('#inviteFriends').modal('hide');
            getChatRoomInfo(channel_no)
        }
    });
}

//记录访问
function getHistory() {
    $.ajax({
        url: '/api/history/',
        type: 'get',
        success: function () {
        }
    })
}
