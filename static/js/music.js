function MusicPlayerInit(element) {
    const player_id = element + '_player'
    $(element).append(`<div id="${player_id}"></div><hr>`)
    var ap = new APlayer({
        container: document.getElementById(player_id),
        mini: false,
        autoplay: false,
        theme: '#FADFA3',
        loop: 'all',
        order: 'random',
        preload: 'auto',
        volume: 0.5,
        mutex: true,
        listFolded: false,
        listMaxHeight: 90,
        lrcType: 1,
        audio: [
            {
                name: '霓虹甜心',
                artist: '马赛克乐队',
                url: 'http://m10.music.126.net/20200807110700/c359ad7702861741032a60549dcd66b8/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a',
                cover: 'cover1.jpg',
                lrc: '[00:00.000] 作曲 : 夏颖/卓越\n[00:01.000] 作词 : 夏颖/卓越\n[00:07.947]霓虹甜心 - 马赛克乐队\n[00:12.700]词：夏颖&卓越\n[00:16.204]曲：夏颖&卓越\n[00:17.817]编曲：卓越\n[00:34.566]制作&混音：Wouter Vlaeminck\n[00:39.825]今夜我用尽所有的方式\n[00:43.576]才得到你的名字\n[00:48.071]此刻芳心要怎样才不流失\n[00:52.075]在这多彩的舞池\n[00:56.068]霓虹下你的影子那么美\n[01:00.072]我感觉我的心在动\n[01:04.574]你慢慢靠近耳边说了句 baby\n[01:08.321]我闻到你的香味\n[01:12.573]darling 你快来救救我\n[01:16.576]darling darling save me\n[01:20.328]darling 进入了音乐里\n[01:40.327]沉醉在这样的夜里\n[01:44.570]你是注定派给我的天使\n[01:48.826]抚慰我不安的种子\n[01:53.070]让这枯萎的生活重发新枝\n[01:57.073]爱是最美的情诗\n[02:00.825]霓虹下你的影子那么美\n[02:05.071]我感觉我的心在动\n[02:09.324]你慢慢靠近耳边说了句 baby\n[02:13.327]我闻到你的香味\n[02:17.322]daring 你快来救救我\n[02:20.572]darling darling save me\n[02:24.825]darling 进入了音乐里\n[02:29.071]沉醉在这样的夜里\n[02:33.324]darling 你快来救救我\n[02:37.329]darling darling save me\n[02:42.076]darling 进入了音乐里\n[02:46.580]沉醉在这样的夜里\n[02:49.821]就在转身的一瞬间\n[02:53.825]你性感的占领我世界\n[02:58.330]心跳已融化在音乐\n[03:02.323]告诉你我的感觉\n[03:09.077]daring 你快来救救我\n[03:12.076]darling darling save me\n[03:16.823]darling 进入了音乐里\n[03:20.827]沉醉在这样的夜里\n[03:26.077]darling 你快来救救我\n[03:29.074]darling darling save me\n[03:33.576]darling 进入了音乐里\n[03:36.828]沉醉在这样的夜里\n[03:39.078]沉醉在这样的夜里\n[03:43.822]沉醉在这样的夜里\n',
                theme: '#ebd0c2'
            },
            {
                name: 'name2',
                artist: 'artist2',
                url: 'http://m10.music.126.net/20200807110700/c359ad7702861741032a60549dcd66b8/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a',
                cover: 'cover2.jpg',
                lrc: 'lrc2.lrc',
                theme: '#46718b'
            },
            {
                name: 'name3',
                artist: 'artist2',
                url: 'http://m10.music.126.net/20200807110700/c359ad7702861741032a60549dcd66b8/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a',
                cover: 'cover2.jpg',
                lrc: 'lrc2.lrc',
                theme: '#46718b'
            }
        ]
    });
    ap.on('ended',function () {
        ap.list.remove(ap.list.index)
    })
    ap.on('error', function () {
        ap.list.remove(ap.list.index)
    })
    return ap
}

function addMusicList(ap,music_info) {
    ap.list.add(music_info)
}
function get() {

}
