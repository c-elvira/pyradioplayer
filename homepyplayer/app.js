var http = require('http');
var fs = require('fs');
var net = require('net');

var END_TRAME = 'FINTRAME'

// Chargement du fichier index.html affiché au client
var server = http.createServer(function(req, res) {
    fs.readFile('./index.html', 'utf-8', function(error, content) {
        res.writeHead(200, {"Content-Type": "text/html"});
        res.end(content);
    });
});


try {
    var client = new net.Socket();
    client.connect(10000, '127.0.0.1');
    client.once( "connect", function () {
        console.log( 'Client: Connected to port ' + 10000 );
    });

}
catch (exception) {
    return exception.code;
}

// Chargement de socket.io
var io = require('socket.io').listen(server);
var ioClient = require('socket.io-client')

io.sockets.on('connection', function (socket, pseudo) {
    // Quand un client se connecte, on lui envoie un message
    socket.emit('message', 'Vous êtes bien connecté !');
    // On signale aux autres clients qu'il y a un nouveau venu
    socket.broadcast.emit('message', 'Un autre client vient de se connecter ! ');

    socket.pseudo = 'someone';

    // Dès qu'on reçoit un "message" (clic sur le bouton), on le note dans la console
    socket.on('message', function (message) {
        // On récupère le pseudo de celui qui a cliqué dans les variables de session
        console.log(socket.pseudo + ' me parle ! Il me dit : ' + message);
    }); 

    // play
    socket.on('play', function (message) {
        // On récupère le pseudo de celui qui a cliqué dans les variables de session
        console.log(socket.pseudo + ' me parle ! Il me dit : ' + 'play musique');
        client.write('play' + END_TRAME);
    });

    // pause
    socket.on('pause', function (message) {
        // On récupère le pseudo de celui qui a cliqué dans les variables de session
        console.log(socket.pseudo + ' me parle ! Il me dit : ' + 'pause musique');
        client.write('pause' + END_TRAME);
    });

    // volume
    socket.on('volume', function (message) {
        // On récupère le pseudo de celui qui a cliqué dans les variables de session
        console.log(socket.pseudo + ' me parle ! Il me dit : ' + 'volume ' + message);
        client.write('volume ' + message + END_TRAME);
    });
});

server.listen(8080);