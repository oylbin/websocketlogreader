websocketlogreader
==================

网页里使用websocket读取后台日志并实时展示

## 使用方式

1. 后台启动websocket(需要 cherrypy & ws4py 支持)

        python websocketlogserver.py

1. 网页里加载 websocketlogreader.js

        <script src="websocketlogreader.js"></script>

        <script type='text/javascript'>

        var websocket = 'ws://192.168.1.198:9001/ws';
        var background_task_pid = 1234;
        var background_task_log = '/var/log/some.log';
        $("#logs").websocketlogreader({
            websocket:websocket
            ,pid:background_task_pid
            ,logfile:background_task_log
            ,onclose:function(evt){
                // background task finished
            }
        });

        </script>
