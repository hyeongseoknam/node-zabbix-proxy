var redis= require('redis');
const fs = require('fs');
var isRedisConnected= false;
var client = redis.createClient();
client.on('connect', function(){
  isRedisConnected = true;
});

var exports = module.exports={};
exports.get = function(request_type){
    return handlers[request_type];
}

var handlers = {
    'active checks': function(request, callback){
        fs.readFile('./resp_active_checks.json', 'utf8', function (err, data) {
            if (err) throw err;
            callback( JSON.parse(data) );
        });   
    },
    'agent data_parse': function(request, callback){
        if (isRedisConnected){
            var samples= request.data;
            var clock = request.clock;
            var multi = client.multi();
            for(var i in samples){
                var sample = samples[i];
                var host = sample.host;
                var key = sample.key;
                var value = sample.value;
                if(sample.clock){
                    clock = sample.clock;
                }
                var host_key = host+'/'+key;
                var clock_value= clock + ':'+value;

                multi.rpush(host_key, clock_value ); 
            }
            multi.exec(function(err, replies){
                var resp = {
                    "response":"success",
                    "info":"Processed "+samples.length+" Failed 0 Total "+samples.length+" Seconds spent 0.002070"
                };
                callback( resp);
            });
        }

        return ;
    },
    'agent data': function(request, callback){
        if (isRedisConnected){
            client.rpush('zabbix_agent_stream', request.rawBody);
        }

        return ;
    }
};


