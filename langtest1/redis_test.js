var redis= require('redis');
var isRedisConnected= false;
var client = redis.createClient();
client.on('connect', function(){
    isRedisConnected = true;
    var milliseconds = ''+(new Date).getTime();
    client.rpush('times',milliseconds, function(err, reply){
        console.log('err:'+err);
        client.lrange('times',0,-1, function(err, reply){
           
            console.log('client.get err:'+err);
            console.log(reply);
        });
    });
});




