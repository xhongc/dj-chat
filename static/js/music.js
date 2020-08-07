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
        volume: 0.7,
        mutex: true,
        listFolded: false,
        listMaxHeight: 90,
        lrcType: 1,
    });
    ap.on('ended', function () {
        ap.list.remove(ap.list.index)
    })
    ap.on('error', function () {
        ap.list.remove(ap.list.index)
    })
    return ap
}

function addMusicList(ap, music_info) {
    ap.list.add(music_info)
}

function get() {

}
