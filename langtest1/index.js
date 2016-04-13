var net = require('net');

var handlers = {'active checks': function(){
        return {
            "response":"success",
            "data":[
            {
                "key":"log[\/home\/zabbix\/logs\/zabbix_agentd.log]",
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
    'agent data': function(){
        return {
            "response":"success",
            "info":"Processed 2 Failed 0 Total 2 Seconds spent 0.002070"
        };
    }
};

net.createServer(function(socket){
    socket.name = socket.removeAddress+":"+socket.remotePort
    //var buffer= new Buffer(2048);

    socket.on('data', function(data){
        console.log(data);
        //buffer.write(data);
        if( data.length > 4){
            var payload = parse(data);
            console.log('payload:'+payload);
            if (payload){
                console.log(payload.request);
                resp = handlers[payload.request]();
                response(socket, resp );           
            }
            socket.destroy();

        }
    });

    socket.on('end', function(data){

    });

    function parse(buffer){
        console.log('buffer.length:'+buffer.length);
        if (buffer.length > 13 &&
            String.fromCharCode(buffer[0]) == 'Z' &&
            String.fromCharCode(buffer[1]) == 'B' &&
            String.fromCharCode(buffer[2]) == 'X' &&
            String.fromCharCode(buffer[3]) == 'D' &&
            buffer[4] == 0x01){
            var payload_length = buffer[5];
            payload_length += buffer[6]<< 8;
            payload_length += buffer[7]<< 16;
            payload_length += buffer[8]<< 24;
            payload_length += buffer[9]<< 32;
            payload_length += buffer[10]<< 40;
            payload_length += buffer[11]<< 48;
            payload_length += buffer[12]<< 56;

            console.log('payload length:'+payload_length);
            if (buffer.length == 13+ payload_length){
                return JSON.parse(buffer.toString('utf-8', 13, 13+payload_length));
            }
        }
    }

    function response(socket, resp){
        var jsonResp = JSON.stringify(resp);
        var length = jsonResp.length;
        var output_list = [];
        output_list.push('Z'.charCodeAt(0));
        output_list.push('B'.charCodeAt(0));
        output_list.push('X'.charCodeAt(0));
        output_list.push('D'.charCodeAt(0));
        output_list.push(0x01);
        output_list.push(length & 0xFF) ;   
        output_list.push(length >> 8 & 0xFF) ;   
        output_list.push(length >> 16 & 0xFF) ;   
        output_list.push(length >> 24 & 0xFF) ;   
        output_list.push(0) ;   
        output_list.push(0) ;   
        output_list.push(0) ;   
        output_list.push(0) ;   

        for(var i in jsonResp){
            output_list.push(jsonResp.charCodeAt(i));
        }
        var outputBuf = new Buffer(output_list);
        console.log('total size:'+outputBuf.length);
        console.log('payload size:'+jsonResp.length);
        console.log('Ouptput buffer:'+outputBuf);
        
        socket.write(outputBuf);

    }


}).listen(10051);
