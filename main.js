var host = 'http://localhost:3001';

var socket = io(host);
var graphs = {};
var graphData = {};

var zip = function (a, b) {
  return a.map(function (e, i) {
    return [e, b[i]];
  });
}

socket.on('data', function (data) {
  for (var key in data) {
    if (key === 'timestamp') continue;
    if (!graphData.hasOwnProperty(key)) {
      var g = $('<div style="width: 90%; margin: 10px auto;"></div>');
      $('body').append(g);
      g.attr('id', 'graph_' + key);
      graphData[key] = zip(data.timestamp, data[key]);
      console.log(key, graphData[key]);
      graphs[key] = new Dygraph(g[0], graphData[key], {
        title: key,
        labels: ['Timestamp', key]
      });
    } else {
      var newData = zip(data.timestamp, data[key]);
      //Don't use concat - it will make new array everytime it is called.
      newData.forEach(function (d) {graphData[key].push(d)});
      var end = data.timestamp[data.timestamp.length - 1];
      var start = Math.max(0, end - 2000);
      graphs[key].updateOptions({'file': graphData[key], dateWindow: [start, end]});
    }
  }
});