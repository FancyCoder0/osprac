

# hw6

任路遥 1500012787



master的对外web server的API接口使用flask实现。具体的API接口见API。

对于master和slave之间的通信使用了RPC方法。同时编写了较为有效的单元测试，测试结果见Test。



### How to Run

```bash
# in slave dir: /slave
# 在对应的/slave/run.py中修改slave_id和slave_ip为对应节点的属性
sudo python3 run.py
```

```bash
# in master dir: /master
sudo python3 manage.py runserver --host 0.0.0.0 
```



### API

可以参考[test_basics.py](https://github.com/luyao-os/osprac/blob/master/hw6/master/tests/test_basics.py)

/

![index](pic/index.jpg)


/job/task

``` json
{ 
    "name" : "task1",  # 任务名称           

    "commandLine": "sleep 10 && echo 10", # 命令行参数

    "outputPath": "data/output.txt", # 输出路径，默认为data/output.txt

    "logPath": "data/log.txt", # 日志路径，默认为data/log.txt

    "maxRetryCount": "2", # 重试次数，默认为0
    
    # 资源限制
    "resource": {
        "cpu": "0,1", # cpu限制
        "memeory": "512M", # 内存限制
    },
    
    "packagePath": "data/testdir", # 程序执行所需的文件包，挂载到了对应的/home目录下

    "timeout": "21600", # 超时时限(秒），默认为60s

    "image": "my-ubuntu", # 镜像名称，默认为新建一个空的LXC镜像，注意这里若有参数，则需要保证镜像在本地存在
}

```



/job/status

``` json
{
    "name" : "task1" # 任务名称   
}
```

/job/kill

``` json
{
    "name" : "task1" # 任务名称   
}
```



### Test

``` bash
# in slave dir: /slave
sudo python3 run.py
```

```bash
# in master dir: /master
sudo python3 manage.py test
```

单节点单元测试结果
![test](pic/test.jpg)

多节点单元测试结果
![test2](pic/multi_slaves_test.png)

多节点手动测试结果
![test3](pic/index2.png)

