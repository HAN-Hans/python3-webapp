# ！/user/bin/python3
# -*- cofing:utf-8 -*-

'''
	watch通过Observer和events自动检查www目录下的.py文件的修改情况
用该脚本启动app.py,则当前目录下任意.py文件被修改后,服务器将自动重启
'''

import os, sys, time
import subprocess		# 该模块提供了派生新进程的能力，实现进程的启动和终止
# watchdog可以利用操作系统的API来监控目录文件的变化，并发送通知
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 日志输出，[Monitor]。。。
def log(s):
	print('[Monitor] %s' % s)

# 自定义的文件系统事件处理器
class MyFileSystemEventHander(FileSystemEventHandler):
	"""docstring for MyFileSystemEventHander"""
	def __init__(self, fn):
		super(MyFileSystemEventHander, self).__init__()
		self.restart = fn
	def on_any_event(self, event):
		if event.src_path.endswith('.py'):
			log('python source file changed: %s' % event.src_path)
			self.restart()


command = ['echo', 'ok']
process = None

def kill_process():
	global process
	if process:
		log('Kill process [%s]...' % process.pid)
		# process指向一个Popen对象,在start_process函数中被创建
        # 通过发送一个SIGKILL给子程序, 来杀死子程序. SIGKILL信号将不会储存数据, 此处也不需要
        # wait(timeout=None),等待进程终止,并返回一个结果码. 
		process.kill()
		process.wait()
		log('Process ended with code %s' % process.returncode)
		process = None

def start_process():
	global process, command
	log('Start process %s...' % ' '.join(command))
	# subprocess.Popen是一个构造器, 它将在一个新的进程中执行子程序
    # command是一个list, 即sequence. 此时, 将被执行的程序应为序列的第一个元素, 此处为python
	process = subprocess.Popen(command, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr)

def restart_process():
	kill_process()
	start_process()

def start_watch(path, callback):
	observer = Observer()		# 创建监视器对像
	# 为监视器对象安排时间表, 即将处理器, 路径注册到监视器对象上
    # 重启进程函数绑定到处理器的restart属性上
    # recursive=True表示递归, 即当前目录的子目录也在被监视范围内
	observer.schedule(MyFileSystemEventHander(restart_process), path, recursive = True)
	observer.start()		# 启动监视器
	log('Watch directory %s...' % path)
    # 启动进程, 通过调用subprocess.Popen方法启动一个python3子程序的进程
	start_process()
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

if __name__ == '__main__':
	argv = sys.argv[1:]
	if not argv:
		print('Usage: python pymonitor your-script.py')
		exit(0)
	if argv[0] != 'python':
		argv.insert(0, 'python')
	command = argv	# 将输入参数赋给command, 之后将用command构建shell命令
	path = os.path.abspath('.')	# 获取当前目录的绝对路径表示.'.'表示当前目录
	start_watch(path, None)


