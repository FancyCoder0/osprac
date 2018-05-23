

# hw6

任路遥 1500012787



### Usage

/job/task

``` json
{ 
    "name" : "task1",             

    "commandLine": "sleep 10 && echo 10",

    "outputPath": "data/output.txt",

    "logPath": "data/log.txt",

    "maxRetryCount": "2", 

    "timeout": "21600",

    "image": "my-ubuntu",
}

```

/job/status

``` json
{
    "name" : "task1"
}
```

/job/kill

``` json
{
    "name" : "task1"
}
```



### Test

in slave dir

``` bash
sudo python3 run.py
```



in master dir

```bash
sudo python3 manage.py test
```

