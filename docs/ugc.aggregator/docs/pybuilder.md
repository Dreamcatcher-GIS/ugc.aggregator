# pybuilder目录
## virtualenv路径
E:\PythonWorkspace\ugc\ugc.venv

## pybuilder路径
E:\PythonWorkspace\ugc\ugc.venv\Scripts\

# pybuilder脚本
## 进入venvShell
workon ugc.venv

## 执行默认build文件
pyb_.exe

## 执行默认build文件，并打印unittest错误详情
pyb_.exe -v

## 新增测试项目
pyb_.exe  --start-project

## 发布
pyb_.exe install_dependencies publish

# pybuilder树状目录介绍
src/main/python：源码
src/main/scripts：可执行脚本
src/main/unittest：单元测试
