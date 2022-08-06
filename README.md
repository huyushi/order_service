一：安装和配置supervisor
1. 安装命令 
brew install supervisor 

2.supervisor安装完成后，mac系统会默认在 /usr/local/bin 路径下生成下面三个命令：
(api_doc) yushideMacBook-Pro:order_service huyushi$ ls /usr/local/bin/|grep super
echo_supervisord_conf      # 用来生成配置supervisord.conf文件 
supervisorctl                        # supervisord  客户端工具 
supervisord			    # supervisord  服务器

3.supervisor安装完成后，会自动在 /usr/local/etc/ 路径下生成一个supervisord.conf配置文件，也可以自己手动用命令生成supervisord.conf配置文件，命令如下:（echo_supervisord_conf > /etc/supervisord.conf ）
(api_doc) yushideMacBook-Pro:order_service huyushi$ ls  /usr/local/etc  | grep super
supervisord.conf

4.查看supervisord.conf配置文件，并修改inet_http_server配置，把port前面的;注释去掉，这个配置是supervisord的web管理界面,如果把用户和密码注释都去掉的话，登录的时候需要输入用户名和密码，因为前端会有一个basic auth, 如果不要去掉，就不需要认证


5.手动在/usr/local/etc/目录下创建supervisor.d文件，然后在这个目录下面编写supervisord需要管理的子进程的配置文件
(api_doc) yushideMacBook-Pro:order_service huyushi$ cd /usr/local/etc/
(api_doc) yushideMacBook-Pro:etc huyushi$ mkdir supervisor.d
(api_doc) yushideMacBook-Pro:etc huyushi$ cd supervisor.d
(api_doc) yushideMacBook-Pro:etc huyushi$ vi web.ini

# web.ini
[program:uwsgi]
directory = /Users/huyushi/Desktop/order_service ;  # cd到工作目录
command = /Users/huyushi/.pyenv/versions/api_doc/bin/uwsgi --ini uwsgi/uwsgi.ini ; # 启动子进程命令
process_name=%(program_name)s ; # 子进程名称
stopsignal=INT ; # 如果没有设置这个参数，当supervisorctl stop uwsgi的时候，并不会完全杀死uwsgi进程，uwsgi会自动再重启
numprocs = 1 ;
autostart = true ;
startsecs = 5 ;
autorestart = true ;
startretries = 3 ;
user = huyushi ; # 用户，切记一定是启动supervisor进程的用户
redirect_stderr = true ;
stdout_logfile_maxbytes = 20MB ;
stdout_logfile_backups = 20 ;
stdout_logfile = /usr/local/etc/supervisor.d/web.log  # uwsgi输出日志, 需要提前创建该文件


(api_doc) yushideMacBook-Pro:etc huyushi$ vi celery.ini
[program:celery]
directory = /Users/huyushi/Desktop/order_service ;
command = /Users/huyushi/.pyenv/versions/api_doc/bin/celery -A order_service worker -l info ;
process_name=%(program_name)s ;
numprocs = 1 ;
autostart = true ;
startsecs = 5 ;
autorestart = true ;
startretries = 3 ;
user = huyushi ;
redirect_stderr = true ;
stdout_logfile_maxbytes = 20MB ;
stdout_logfile_backups = 20 ;
stdout_logfile = /usr/local/etc/supervisor.d/celery.log  # celery输出日志, 需要提前创建该文件


6.启动Supervisor服务，Supervisor是父进程，当Supervisor父进程启动的时候，会去读取supervisor.d文件夹下面子进程的配置文件，然后根据子进程的配置文件里面的启动命令去启动子进程

启动supervisord命令：
/usr/bin/supervisord  -c   /usr/local/ect/supervisord.conf

7.supervisorctl查看子进程状态,发现uwsgi和celery进程都启动了


8.去supervisord的web 界面确认一下是否子进程都起来了



二：遇到的坑
1: 当没有用虚拟环境里面的supervisord依赖启动supervisord进程，会导致kill -9  ID杀不死supervisord，因为杀死又会自动起来
 解决方案: brew services stop supervisor

2.当使用supervisorctl stop uwsgi停止uwsgi进程的时候，不会全部杀死uwsgi进程，打开supervisord.log文件出现以下内容，原因是
因为uwsgi 收到kill命令的时候，会自动重启，杀不死。



解决方案： 在web.ini配置文件中添加stopsignal=INT配置, 然后再supervisorctl update


参考资料： https://blog.csdn.net/m0_37422289/article/details/82997019

3. supervisorctd进程无法启动uwsgi进程，日志文件冲突导致
解决方案: 注释掉uwsgi.ini配置文件里面的日志文件配置


参考资料: https://zhuanlan.zhihu.com/p/65040410

supervisorctl 常用命令：
关闭supervisord服务
supervisorctl shutdown         

查看所有进程的运行状态
supervisorctl status

#查看某一进程的运行状态
supervisorctl status　进程名

#启动某一进程
supervisorctl start 进程名

#启动所有进程
supervisorctl start all

#停止某一进程
supervisorctl stop 进程名

#停止所有进程
supervisorctl stop all

#重启某一进程
supervisorctl restart 进程名

#重启所有进程
supervisorctl restart all

#新增进程后，更新进程(不影响其他进程运行)
supervisorctl update

#新增进程后，重启所有进程
supervisorctl reload








