var net = require('net');
var handler = require('./handler.js');

net.createServer(function(socket){
    socket.name = socket.removeAddress+":"+socket.remotePort
    socket.bufs= [];
    socket.idx = 0;
    //var buffer= new Buffer(2048);

    socket.on('data', function(data){
        var newbuf = new Buffer(data.length);
        data.copy(newbuf);
        socket.bufs.push(newbuf);
        socket.idx += data.length;
        if( socket.idx > 13){
            var payload = parse(socket, function(payload){
                console.log(payload.request);
                handler.get(payload.request)(payload, function(resp){
                    response(socket, resp );           
                });
            });
        }
    });

    socket.on('end', function(data){

    });

    function parse(socket, callback){
        var bufs = socket.bufs;
        if(!socket.payload_length){
            var header=[];
            var header_byte_count = 0;
            var buffer_count=0;
            while(header_byte_count < 14){
                var buffer = bufs[buffer_count];
                buffer_count += 1;
                var buffer_byte_count=0;
                while ( header_byte_count < 14 && buffer_byte_count < buffer.length ){
                    header.push(buffer[buffer_byte_count]);
                    buffer_byte_count +=1;
                    header_byte_count +=1;
                }
            }
            
            if (String.fromCharCode(header[0]) == 'Z' &&
                String.fromCharCode(header[1]) == 'B' &&
                String.fromCharCode(header[2]) == 'X' &&
                String.fromCharCode(header[3]) == 'D' &&
                header[4] == 0x01){
                var payload_length = header[5];
                payload_length += header[6]<< 8;
                payload_length += header[7]<< 16;
                payload_length += header[8]<< 24;
                payload_length += header[9]<< 32;
                payload_length += header[10]<< 40;
                payload_length += header[11]<< 48;
                payload_length += header[12]<< 56;

                socket.payload_length = payload_length;
        console.log('parse step -4:'+payload_length);
            }else{
                console.log('parse step -5');
                socket.end();
            }
        }
        console.log('parse step -6');
        var payload_length = socket.payload_length;
        var until_now = socket.idx-13;
        console.log('parse step -6.1:'+until_now);
        if (payload_length == until_now){
            console.log('parse step -7');
            var buf = new Buffer(payload_length);
            var header_byte_count = 0;
            var buffer_count=0;
            var buffer_byte_count=0;
            while(header_byte_count < 14){
            console.log('parse step -8');
                var buffer = bufs[buffer_count];
                buffer_byte_count=0;
                while ( header_byte_count < 14 && buffer_byte_count < buffer.length ){
                    buffer_byte_count +=1;
                    header_byte_count +=1;
                    console.log('parse step -9');
                }
                if(header_byte_count < 14){
                    buffer_count += 1;
                }
            }       
            var whead = 0;
            if (buffer_byte_count < bufs[buffer_count].length){
                whead = buf.write(bufs[buffer_count].toString('utf8', buffer_byte_count-1, bufs[buffer_count].length));
            }
            buffer_count +=1;
            for(var i= buffer_count; i < bufs.length; i+=1){
                whead += buf.write(bufs[i].toString('utf8'), whead);
                    console.log('parse step -10');
            }
            console.log('parse step -10.1:');
            console.log(buf.toString('utf-8'));
            var jsonresp = JSON.parse(buf.toString('utf-8'));
            callback(jsonresp);
        }
                    console.log('parse step -11');
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
        
        socket.end(outputBuf);

    }


}).listen(10051);
