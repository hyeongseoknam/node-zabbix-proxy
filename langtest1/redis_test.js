var redis= require('redis');
var isRedisConnected= false;
var client = redis.createClient();
client.on('connect', function(){
    isRedisConnected = true;
    var milliseconds = (new Date).getTime();
    client.rpush('times',milliseconds, function(err, reply){
        client.get('times', function(err, reply){
            console.log(reply);
        });
    });
});




