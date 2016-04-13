var redis= require('redis');
var isRedisConnected= false;
var client = redis.createClient();
client.on('connect', function(){
  isRedisConnected = true;
});

var exports = module.exports={};
exports.get = function(request_type){
	return handlers[request_type];
}

var handlers = {'active checks': function(request){
        return {
            "response":"success",
            "data":[
            {
                "key":"log[\/var\/log\/syslog]",
                "delay":"30",
                "lastlogsize":"0"
            },
            {
                "key":"agent.version",
                "delay":"600"
            }
            ]
        } ;
    },
    'agent data': function(request){
        return {
            "response":"success",
            "info":"Processed 2 Failed 0 Total 2 Seconds spent 0.002070"
        };
    }
};


