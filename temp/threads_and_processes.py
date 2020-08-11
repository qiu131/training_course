#### 进程与线程

'''
# # daemon守护进程，父进程终止后自动终止
import multiprocessing, time,os


def sing(interval):
    for i in range(3):
        print('singing ')
        time.sleep(interval)


def dance(interval):
    for i in range(3):
        print('dancing ')
        time.sleep(interval)


def main():
    p1 = multiprocessing.Process(target=sing, args=(1,))
    p2 = multiprocessing.Process(target=dance, args=(1,))
    p1.start()
    p2.start()
    print('current process: {}'.format(os.getpid()))

if __name__ == '__main__':
    main()
'''

'''
##并发安全问题，进程并发访问同一资源时，会导致进程安全性问题
from multiprocessing import Process, Lock, Value
import time, os, random, json
def check():
    time.sleep(random.randint(1, 3))
    with open('tickets.db','r',encoding='utf-8') as fd:
        dict1 = json.load(fd)
        print('{}查询余票数为{}'.format(os.getpid(), dict1['count']))
def get():
    """购买票"""
    with open('tickets.db', 'r', encoding='utf-8') as fd:
        dict1 = json.load(fd)
        time.sleep(1)
    if dict1['count'] > 0:
        dict1['count'] -= 1
        with open('tickets.db', 'w', encoding='utf-8') as fd:
            json.dump(dict1, fd)
            print('{}购买成功'.format(os.getpid()))
    else:
        print('{}票已售完'.format(os.getpid()))
def init_db():
    with open('tickets.db', 'w', encoding='utf-8') as fd:
        json.dump({'count':100}, fd)
def task():
    check()
    get()
def main():
    print('主进程开始')
    if not os.path.exists('tickets.db'):
        init_db() # 初始化数据
    for i in range(100):
        p1 = Process(target=task)
        p1.start()
    print('主进程结束')

if __name__ == '__main__':
    main()
'''

'''
#使用同步锁解决问题
from multiprocessing import Process, Lock, Value
import time, os, random, json

def check():
    time.sleep(random.randint(1, 3))
    with open('tickets.db','r',encoding='utf-8') as fd:
        dict1 = json.load(fd)
        print('{}查询余票数为{}'.format(os.getpid(), dict1['count']))

def get():
    """购买票"""
    with open('tickets.db', 'r', encoding='utf-8') as fd:
        dict1 = json.load(fd)
    time.sleep(1)
    if dict1['count'] > 60:
        dict1['count'] -= 1
        with open('tickets.db', 'w', encoding='utf-8') as fd:
            json.dump(dict1, fd)
            print('{}购买成功'.format(os.getpid()))
    else:
        print('{}票已售完'.format(os.getpid()))

def init_db():
    with open('tickets.db', 'w', encoding='utf-8') as fd:
        json.dump({'count':100}, fd)

def task(lock):
    lock.acquire()
    check()
    get()
    lock.release()

def main():
    print('主进程开始')
    # init_db()
    lock = Lock()
    for i in range(100):
        p1 = Process(target=task, args=(lock,))
        p1.start()
    p1.join()
    print('主进程结束')

if __name__ == '__main__':
    main()
'''

'''
##队列的原理
from multiprocessing import Queue
queue = Queue(3)
print('队列长度：{}'.format(queue.qsize()))
queue.put(1) # 存放数据
queue.put(2)
queue.put(3)
print('队列长度：{}'.format(queue.qsize()))
print('队列已满：{}'.format(queue.full()))
result = queue.get() # 从队列删除一个数据,FIFO,返回值为删除的数据
print(result) # 1
result = queue.get() # 从队列删除一个数据,FIFO,返回值为删除的数据
print(result) # 1
result = queue.get() # 从队列删除一个数据,FIFO,返回值为删除的数据
print(result) # 1
print('队列已空：{}'.format(queue.empty()))
# result = queue.get(block=False) # 不阻塞的从队列取数据,如果队列空了直接抛出 Empty 异常
# print(result) # 1
'''

'''
# 主进程与子进程、子进程与子进程之间不能通过全局变量来共享数据
from multiprocessing import Queue, Process
import time
import random
import os
class BaoZi(object):
    def __init__(self, name):
        self.name = name
def producer(queue, name):
    """生产者"""
    for i in range(1,10):
        time.sleep(random.random())
        baozi = BaoZi('第{}个{}'.format(i, name))
        queue.put(baozi)
        print('进程{}生产了第{}个{}'.format(os.getpid(), i, name))
def consumer(queue):
    """消费者"""
    while True:
        time.sleep(random.randint(1, 2))
        try:
            baozi = queue.get(block=True, timeout=5)
        except:
            break
        print('进程{}消费了{}'.format(os.getpid(), baozi.name))
def main():
    print('主进程开始执行')
    queue = Queue(5)
    # 生产包子
    p1 = Process(target=producer, args=(queue, '豆沙包'))
    p2 = Process(target=producer, args=(queue, '牛肉包'))
    p3 = Process(target=producer, args=(queue, '汤包'))
    p1.start()
    p2.start()
    p3.start()
    # p1.join() 不能放这里，因为 queue 放 5 个包子后就不能再放了，就阻塞在这了。需要放在消费代码的后面。
    # 消费包子
    c1 = Process(target=consumer, args=(queue,))
    c2 = Process(target=consumer, args=(queue,))
    c1.start()
    c2.start()
    p1.join() #是否等待子进程执行结束，或等待多少秒
    print('主进程结束执行')
if __name__ == '__main__':
    main()
'''

#进程池类Pool
#异步执行(非阻塞) p.apply_async(func [, args [, kwargs]])
# 异步的执行模式，才是可以实现并行效果的模式，支持callback回调函数，
# 当一个进程没有执行完毕，没有返回结果，异步执行的模式并不会对主进程进行阻塞！
#补充一点！虽然 apply_async是非阻塞的，但其返回结果的get方法却是阻塞的，
# 如使用result.get()会阻塞主进程！get会让程序出现阻塞直到等到值
# from multiprocessing import Process, Pool
# import time
# def fun(num):
#     # time.sleep(1)
#     #print(num)
#     return num * 2
# def main():
#     begin = time.time_ns()
#     print('主进程开始执行')
#     nums = []
#     pool = Pool(4)
#     for i in range(1, 10):
#         result = pool.apply_async(fun, (i, )) # 异步执行,4 个进程之间是并发执行的
#         #nums.append(result.get()) # 通过 ApplyResult 类型的对象的 get 方法获取到 fun 方法的返回值
#         nums.append(result) # 通过 ApplyResult 类型的对象的 get 方法获取到 fun 方法的返回值
#         #print(type(result)) # ApplyResult 类型
#     # pool.close() # 关闭进程池，保证的是没有新的任务进入进程池
#     # pool.join() # 阻塞，直到队列中的任务都完成，检测的是子进程里面的任务结束，而不是子进程的结束
#     # for num in nums:
#     #     print(num.get())
#     end = time.time_ns()
#     print('主进程结束执行')
#     print('It takes {}'.format(end-begin))
# if __name__ == '__main__':
#     main()

'''
# 同步执行(阻塞) p.apply(func [, args [, kwargs]])
# 这种模式一般情况下没人会去用，如果进程池使用了这种模式，
# 当进程池的第一个进程执行完毕后，才会执行第二个进程，第二个进程执行完毕后，在执行第三个进程....
# （也就是说这种模式会阻塞主进程！），无法实现并行效果。（不止如此，这种模式还不支持callback回调函数。）
from multiprocessing import Process, Pool
import time
def fun(num):
    # time.sleep(1)
    # print(num)
    return num * 2
def main():
    begin = time.time_ns()
    print('主进程开始执行')
    nums = []
    pool = Pool(4)
    for i in range(1, 10):
        result = pool.apply(fun, (i, )) # 同步执行、阻塞、直到本次任务执行完毕拿到 result
        nums.append(result) # 直接返回 fun 函数的返回值
        #print(type(result)) # fun 方法返回值的类型
    pool.close() # 关闭进程池。
     # pool.join() # apply 方法无需此操作
    # for num in nums:
    #     print(num)
    end = time.time_ns()
    print('主进程结束执行')
    print('It takes {}'.format(end - begin))
if __name__ == '__main__':
    main()
'''


# import threading, time, os
# def task1():
#     for i in range(5):
#         print('子线程生产一个苹果,所属进程为{}'.format(os.getpid()))
#         print('t1线程：{}'.format((threading.current_thread().getName())))
#         time.sleep(10) # 让当前线程睡眠 1 秒
# def task2():
#     for i in range(5):
#         print('子线程消费一个苹果,所属进程为{}'.format(os.getpid()))
#         print('t2线程：{}'.format((threading.current_thread().getName())))
#         time.sleep(10) # 让当前线程睡眠 1 秒
# def main():
#  # 创建线程对象,target 指定执行的方法名称
#     t1 = threading.Thread(target=task1)
#     t2 = threading.Thread(target=task2)
#  # 开启线程,等待获得 cpu 的时间片后开始执行线程
#     t1.start()
#     t2.start()
#     print('主进程:{}'.format(os.getpid()))
#     print('主线程：{}'.format(threading.current_thread().getName()))
#
# if __name__ == '__main__':
#     main()


# import threading, time, os
# def task1(times):
#     for i in range(5):
#         print('{}生产一个苹果,所属进程为{}'.format(threading.currentThread().getName(),
#         os.getpid()))
#         time.sleep(1) # 让当前线程睡眠 1 秒
#     print('子线程{}结束'.format(threading.currentThread().getName()))
# def task2(times, thread_name):
#     threading.currentThread().name = thread_name # 设置线程的名称
#  # threading.currentThread().setName(thread_name) # 设置线程的名称
#     for i in range(5):
#         print('{}消费一个苹果,所属进程为{}'.format(threading.currentThread().getName(),
#         os.getpid()))
#         time.sleep(1) # 让当前线程睡眠 1 秒
#     print('子线程{}结束'.format(threading.currentThread().getName()))
# def main():
#  # 创建线程对象,target 指定执行的方法名称
#     t1 = threading.Thread(target=task1, name='子线程 1', args=(10,)) # name 参数设置线程名称
#     t2 = threading.Thread(target=task2, args=(5, '线程 a'))
#  # 开启线程,等待获得 cpu 的时间片后开始执行线程
#     t1.start()
#     t2.start()
#     print('主线程:{}结束'.format(threading.currentThread().getName())) #
#     threading.currentThread()#获取当前线程
# if __name__ == "__main__":
#     main()


# from threading import Thread, Lock
# import os, time
# total_number = 0
# def task(lock):
#     lock.acquire()
#     for i in range(1000000):
#         global total_number
#         total_number += 1
#     lock.release()
#
# def main():
#     begin = time.time_ns()
#     lock = Lock()
#     t1 = Thread(target=task, args=(lock,))
#     t2 = Thread(target=task, args=(lock,))
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()
#     print(total_number)
#     end = time.time_ns()
#
#     print('cost time {} ns'.format(end-begin))
#
# if __name__ == '__main__':
#     main()

## 生产者与消费者
# from threading import Thread,currentThread
# from queue import Queue
# # 队列，用于线程之间共享数据
# queue = Queue(5)
# def producer():
#     """需要 200 个包子"""
#     print('=====需要 200 个包子======')
#     for i in range(200):
#         queue.put(i+1)
#         print('生产{}个包子'.format(i+1))
# def consumer():
#     baozi = queue.get()
#     print('{}消耗了第{}个包子'.format(currentThread().getName(), baozi))
# def main():
#     # 生产者：产生需求
#     p1 = Thread(target=producer)
#     p1.start()
#     while True:
#         # 消费者，消费需求，也就是生产包子
#         c = Thread(target=consumer)
#         c.start()
# if __name__ == "__main__":
#     main()

## 线程池，系统创建和关闭一个线程的成本比较高，因为它涉及与操作系统的交互。在这种情形下，使用线程池可以很好地
#提升性能。能够很好地复用线程。
# from threading import Thread, currentThread
# from queue import Queue, Empty
# from concurrent.futures import ThreadPoolExecutor
# # 队列，用于线程之间共享数据
# que = Queue(5)
# def producer():
#     """需要 200 个包子"""
#     print('=====需要 200 个包子======')
#     for i in range(200):
#         que.put(i+1)
#         print('{}生产第{}个包子'.format(currentThread().getName(),i+1))
#
# def consumer():
#     try:
#         baozi = que.get(block=True, timeout=5)
#     except Empty:
#         # print("=================")
#         return 0
#     print('{}消耗了了第{}个包子'.format(currentThread().getName(), baozi))
# def main():
#     list1 = []
#     with ThreadPoolExecutor(4) as pool: # 默认是 CPU 的核数 * 5
#     # 生产者：产生需求
#         pool.submit(producer)
#         while True:
#             # if not que.empty():
#             # 消费者，消费需求，也就是生产包子
#             result = pool.submit(consumer) # submit 用于将提交 consumer 方法提交给空闲的线程去执行
#             if result.result() == 0: # result.result() 用于获取线程中 consumer 方法的返回值
#                 break # 如果返回的 0 就说明发生 consumer 方法发生 Empty 异常了。
#
# if __name__ == "__main__":
#     main()

#python的多进程是真实的多进程，而多线程是伪多线程（因为GIL的存在，CPython执行时只有一个线程能获取GIL后得到
# 执行，其他线程必须等待GIL的释放，因此是单线程，无法发挥多核CPU的优势）
# Numpy库是真实的多线程，它绕开了GIL，效率会很高
# def Fibonacci(n):
#     if n == 1 or n ==2:
#         return 1
#     else:
#         return Fibonacci(n-1)+Fibonacci(n-2)
# print(Fibonacci(10))

def fibonacci(n):
    a = 1
    b = 1
    c = 1
    for i in range(1,n-1):
        a = c+b
        c = b
        b = a
    return a
for i in range(1,10):
    print(fibonacci(i))