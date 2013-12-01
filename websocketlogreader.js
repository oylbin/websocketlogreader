// http://stackoverflow.com/questions/3958406/how-to-write-a-simple-jquery-plugin
// http://learn.jquery.com/plugins/basic-plugin-creation/

(function($) {
    if (!$.websocketlogreader) { // check your plugin namespace does not already exist
        $.extend({  //  this will allow you to add your plugin to the jQuery lib
            websocketlogreader: function(elm, command, args) {
                //  keep in mind, right here you might want to do a class or data check to determine which direction this call is going
                //  for example, upon init the plugin on an element you may add the plugin name as a class, 
                //      this way, when it's recalled, you can see it alrady has that class and might be calling a command,
                //          thus make an if statemnt to push the process through
                if(window.WebSocket || window.MozWebSocket){
                    return elm.each(function(index){
                        // do work to each element as its passed through
                        // be sure to use something like
                        //    return elm.each(function(e) { dor work });
                        // as your final statement in order to maintain "chainability"

                        var websocket = command.websocket;
                        var pid = command.pid;
                        var filename = command.logfile;
                        var ws;
                        if (window.WebSocket) {
                            ws = new WebSocket(websocket);
                        }else if (window.MozWebSocket) {
                            ws = MozWebSocket(websocket);
                        }else {
                            alert('您的浏览器不支持web socket，请使用Chrome或者Firefox');
                            return;
                        }

                        $(elm[index]).css({
                            display:'block'
                            ,padding:'9.5px'
                            ,margin:'10px'
                            ,'font-size':'13px'
                            ,'line-height':'20px'
                            ,'word-break':'break-all'
                            ,'word-wrap':'normal'
                            ,'white-space':'pre'
                            ,'background-color':'#f5f5f5'
                            ,border:'1px solid rgba(0,0,0,0.15)'
                            ,overflow:'auto'
                            ,width:'auto'
                        });
                        //.pre-scrollable{max-height:340px,overflow-y:scroll}

                        elm[index].innerHTML = '';
                        ws.onmessage = function(evt){
                            //$(elm[index]).html($(elm[index]).html() + evt.data);
                            elm[index].innerHTML += evt.data;
                        }
                        ws.onclose = function(evt){
                            console.log(evt);
                            if(evt.code!=1000){
                                if(evt.code==1006){
                                    alert("无法连接日志读取WebSocket Server");
                                }else{
                                    alert('Connection closed by server: ' + evt.code + ' "' + evt.reason + '"');  
                                }
                            }
                            command.onclose(evt);
                        }
                        window.setTimeout(function(){
                            ws.send('{"pid":"'+pid+'","filename":"'+filename+'"}');
                        },1000);
                    });
                }else{
                    return elm.each(function(index){
                    });
                }
            }
        });
        $.fn.extend({   //  this gives the chainability functionality seen with $ funcs like: $("#eleID").css("color", "red") <--returns original element object
            websocketlogreader: function(command) {
                return $.websocketlogreader($(this), command, Array.prototype.slice.call(arguments, 1));
            }
        });
        $.websocketlogreader.isAvailable = function(param) {
            if(window.WebSocket || window.MozWebSocket){
                return true;
            }else{
                return false;
            }
        };
    }
})(jQuery);
