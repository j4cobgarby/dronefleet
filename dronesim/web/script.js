var cradar;
var cpid;
let socket = new WebSocket("ws://127.0.0.1:13254")

socket.onmessage = function(event) {
    console.log(event.data);
}

function init() {
    cradar = document.getElementById("radarcanvas");
    var ctx = cradar.getContext("2d");
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.rect(0,0,600,600);
    ctx.fill();

    ctx.strokeStyle = "lime";
    ctx.moveTo(100,100);
    ctx.lineTo(500,500);
    ctx.stroke();
}