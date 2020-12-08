var db = window.indexedDB;

db.open("video_database").onsuccess = function (ev) {
    db = ev.target.result;
    window.setTimeout(getSomeValue, 1000);
};;


function getSomeValue() {
    db.transaction("video_list").objectStore("video_list").getAll().onsuccess = saveObjects;
};

function saveObjects(ev) {
    var objs = ev.target.result;
    for (index = 0; index < objs.length; index++) {
        key = objs[index]['ttid'];
        localStorage.setItem(key, JSON.stringify(objs[index]));
    }
    db.close();
};
