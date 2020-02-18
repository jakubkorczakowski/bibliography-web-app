document.addEventListener('DOMContentLoaded', function (event) {
    var ws_uri = "http://" + document.domain + ":" + location.port;

    var socket = io.connect(ws_uri);

    socket.on("connect", function () {
        console.log("Correctly connected websocket");
    });

    socket.emit("message", {data: "Chyba dziala"});

});