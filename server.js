'use strict'

const io = require('socket.io')(3001);

const numData = 80;

io.on('connection', function (socket) {
  let timestamp = 0;
  let keys =['vel','acc','x','y','z'];
  setInterval(() => {
    let times = [];
    let data = {}
    for (let i = 0; i < numData; i++) {
      times.push(timestamp++);
    }
    for (let k = 0; k < keys.length; k++) {
      data[keys[k]] = [];
      let val = Math.random() - 0.5;
      for (let i = 0; i < numData; i++) {
        data[keys[k]].push(val);
        val += Math.random() - 0.5;
      }
    }
    data.timestamp = times;
    socket.emit('data', data);
    console.log('Data sent ', timestamp);
  }, 200);
});