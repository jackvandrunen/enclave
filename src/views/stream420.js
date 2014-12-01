/*
The client side implementation of Stream420, a thread safe two-way communication protocol for web-based applications and
their servers.

This script has no outside dependencies, and includes:
 - A listener that listens on a specified path, triggering a callback (function) when data is sent from the server via HTML5
   SSE
 - A sender that sends data to the server via AJAX

NOTE: Data is sent and received as an object


SYNTAX TREE:

    stream420
        .Stream (path, callback)  // Sender and receiver, assuming the same 'path' for both of them
            .send (object)
            .close ()  // Close the listener

        .Listener (path, callback)  // The receiver (HTML5 SSE)
            .close ()

        .Sender (path)  // The sender (AJAX)
            .send (object)
*/


var stream420 = {

    Listener: function (path, callbackFunc) {
        var callback = callbackFunc, source = new EventSource(path);
        source.onmessage = function (e) {
            callback(JSON.parse(e.data.trim()));
        };
        this.close = source.close;
    },

    Sender: function (path) {
        var parent = this;
        this.path = path;
        this.send = function (obj) {
            var data = encodeURIComponent(JSON.stringify(obj)), xhr = new XMLHttpRequest();
            xhr.open("POST", parent.path, true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send("data=" + data);
        };
    }

};

stream420.Stream = function (path, callbackFunc) {
    var listener = stream420.Listener(path, callbackFunc), sender = stream420.Sender(path);
    this.send = sender.send;
    this.close = listener.close;
};
