virtualenvwrapper-win
---
## virtualenv配置
安装：pip install virtualenv
新建virtualEnv：virtualenv --no-site-packages venv
进入venvShel：E:\PythonWorkspace\ugc\ugc.venv\Scripts\activate

## virtualenvwrapper安装
linux：pip install  virtualenvwrapper
windows：pip install virtualenvwrapper-win

## virtualenvwrapper配置
安装完毕过后在环境变量里面新建一个WORKON_HOME字段存储虚拟python环境,
WORKON_HOME：E:\PythonWorkspace\venv
环境变量立即生效：cmd中运行set WORKON_HOME=E:\PythonWorkspace\venv

## 常用的一些命令
命令安装在C:\Python27\Scripts\*.bat
*. 创建虚拟环境:mkvirtualenv VirtualenvName
*. 列出所有虚拟环境:Lsvirtualenv
*. 移除虚拟环境:rmvirtualenv VirtualenvName
*. 切换到VirtualenvName环境:workon VirtualenvName
*. 退出当前虚拟环境:deactivate
