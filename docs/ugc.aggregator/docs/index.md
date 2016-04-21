# pybuilder入门项目

[pybuilder官方文档](http://pybuilder.github.io/documentation/tutorial.html)

## pybuilder.helloworld

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs help` - Print this help message.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.


## requirements
logging
gevent
MySQLDB
weibo
selenium
scrapy(依赖lxml)
    
    
## cmd运行配置
新增workspace.path文件到virtualenv目录（E:\PythonWorkspace\ugc\ugc_venv\Lib\site-packages）
``` 
E:\PythonWorkspace\ugc\ugc.aggregator
E:\PythonWorkspace\ugc\ugc.aggregator\src\main\python
```
注意path文件中的模块目录必须有__init__.py文件
## 进入virtualEnv
E:\PythonWorkspace\ugc\ugc_venv\Scripts\activate
## 执行程序
python E:\PythonWorkspace\ugc\ugc.aggregator\src\main\scripts\GeocodingService.py
