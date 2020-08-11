function MusicPlayerInit(element) {
    const player_id = element + '_player'
    $(element).append(`<div id="${player_id}"></div><hr>`)
    var ap = new APlayer({
        container: document.getElementById(player_id),
        mini: false,
        autoplay: false,
        theme: '#FADFA3',
        loop: 'all',
        order: 'list',
        preload: 'auto',
        volume: 0.5,
        mutex: true,
        listFolded: false,
        listMaxHeight: 90,
        lrcType: 1,
    });
    // 禁止切歌
    $('.aplayer-bar-wrap').css("pointer-events", "none")
    $('.aplayer-list').css("pointer-events", "none")
    $('.aplayer-pic').css("pointer-events", "none")
    ap.on('ended', function () {
        var song_index = ap.list.index -1
        if (song_index <0) {
            song_index = 0
        }
        var song_list = ap.list.audios[song_index]
        var song_list_id = song_list ? song_list.id : ''
        console.log('移除song', song_index, song_list_id)
        // 播放结束移除redis里的歌单
        chatSocket.send(JSON.stringify({
            'message': song_list,
            'song_index': song_index,
            'msg_type': 'chat_music',
            'action': 'remove_song',
            'now_song_id': song_list_id,

        }));
        ap.list.remove(song_index)

    })
    //播放错误重新请求
    ap.on('error', function (e) {
        var song_index = ap.list.index
        var song_list = ap.list.audios[song_index]
        var song_list_id = song_list ? song_list.id : ''

        ap.list.remove(song_index)
        console.log('歌曲重新获取url', song_index, ap.list.audios, window.reload_song_id)
        if (!window.reload_song_id) {
            window.reload_song_id = 'yes'
            chatSocket.send(JSON.stringify({
                'message': 'reload_song_url',
                'song_index': song_index,
                'msg_type': 'chat_music',
                'action': 'reload_song_url',
                'now_song_id': song_list_id,
            }));
        } else {
            delete window.reload_song_id
        }

    })
    ap.on('abort', function (e) {
        console.log('abortabortabortabort')
    })
    // ap.on('canplay', function (e) {
    //     console.log('canplay', e)
    // })
    // ap.on('canplaythrough', function (e) {
    //     console.log('canplaythrough', e)
    // })
    ap.on('durationchange', function (e) {
        console.log('durationchange')
    })
    ap.on('emptied', function (e) {
        console.log('emptied')
    })
    ap.on('loadeddata', function (e) {
        console.log('loadeddata')
    })
    ap.on('loadedmetadata', function (e) {
        console.log('loadedmetadata')
    })
    // ap.on('loadstart', function (e) {
    //     console.log('loadstart', e)
    // })
    // ap.on('mozaudioavailable', function (e) {
    //     console.log('mozaudioavailable', e)
    // })
    // ap.on('pause', function (e) {
    //     console.log('pause', e)
    //
    // })
    // ap.on('play', function (e) {
    // })
    // ap.on('playing', function (e) {
    //     console.log('playing', ap.audio.currentTime)
    //
    // })
    ap.on('progress', function (e) {
        console.log('progress')
        ap.play()
        if (window.seek_num) {
            ap.seek(window.seek_num)
            delete window.seek_num;
        }

    })
    // ap.on('seeked', function (e) {
    //     console.log('seeked', ap.audio.currentTime.toString())
    // })
    // ap.on('seeking', function (e) {
    //     console.log('seeking', ap.audio.currentTime.toString())
    // })
    // ap.on('stalled', function (e) {
    //     console.log('stalled')
    // })
    // ap.on('suspend', function (e) {
    //     console.log('suspend')
    // })
    ap.on('timeupdate', function (e) {
        var curr_time = parseInt(ap.audio.currentTime)
        if (curr_time % 5 === 0 && curr_time !== 0) {
            if (window.curr_time_int !== curr_time) {
                // console.log('记录：', curr_time)
                window.curr_time_int = curr_time
                chatSocket.send(JSON.stringify({
                    'message': curr_time.toString(),
                    'song_index': '',
                    'msg_type': 'chat_music',
                    'action': 'update_song',
                    'now_song_id': ap.list.audios[ap.list.index] ? ap.list.audios[ap.list.index].id : '',
                }));
            }
        }
    })
    // ap.on('volumechange', function (e) {
    //     console.log('timeupdate', e)
    // })
    // ap.on('waiting', function (e) {
    //     console.log('timeupdate', e)
    // })
    return ap
}

function addMusicList(ap, music_info, index = null) {
    if (index) {
        ap.list.switch(index);
    } else {
        ap.list.add(music_info)
    }

}

