# University of Illinois/NCSA Open Source License
#
# Copyright (c) 2017 ACM@UIUC
# All rights reserved.
#
# Developed by:	    SIGBot
#                   ACM@UIUC
#                   https://acm.illinois.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# with the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimers.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimers in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the names of the SIGBot, ACM@UIUC, nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this Software without specific prior written permission.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH
# THE SOFTWARE.


from threading import Thread, Condition, Lock


class TaskQueue(Thread):
    '''Task Queue that runs in a separate "thread"'''
    class Promise():
        '''An object that can be waited on'''
        def __init__(self):
            self.condition = Condition()
            self.wait_done = False

        def wait(self):
            '''Wait for the work to be done'''
            with self.condition:
                while not self.wait_done:
                    self.condition.wait()

        def notify(self):
            '''Wake waiters'''
            with self.condition:
                self.wait_done = True
                self.condition.notifyAll()

    class Work():
        '''Represents a piece of work to be done'''
        def __init__(self, func):
            self.func = func
            self.promise = TaskQueue.Promise()

        def __call__(self):
            self.run()

        def run(self):
            self.func()
            self.promise.notify()

    def __init__(self):
        super(TaskQueue, self).__init__()
        self.work_queue = []
        # Condition variable to protect the work queue
        # In the threading library, this acts as both a lock and a condition
        # variable
        self.work_condition = Condition()

        self.shutdown_lock = Lock()
        self.shutdown_ = False
    def __del__(self):
        self.shutdown()

    def run(self):
        '''Start doing work in a separate thread'''

        self.shutdown_lock.acquire()
        while not self.shutdown_:
            self.shutdown_lock.release()

            work = None
            # Make sure to handle the work queue with the lock
            with self.work_condition:
                while len(self.work_queue) == 0:
                    self.shutdown_lock.acquire()
                    if self.shutdown_:
                        self.shutdown_lock.release()
                        return
                    self.shutdown_lock.release()
                    # Wait for values to be available
                    self.work_condition.wait()

                # I just recently found out that this is an atomic operation...
                work = self.work_queue.pop(0)

            if work:
                # Do the work. Arguments should be bound to the function object
                work()

            # Reacquire the lock before we check its value in the loop
            self.shutdown_lock.acquire()
        self.shutdown_lock.release()

    def add_work(self, func):
        '''Add work to the queue

        Arguments:
        work -- a function to be called by the work queue. If the function to
                be called has arguments, use partial application
                (`from functools import partial`)
        '''
        with self.work_condition:
            work = TaskQueue.Work(func)
            self.work_queue.append(work)

            # We're notifying all waiters, but there should only be one
            self.work_condition.notifyAll()
        return work.promise

    def shutdown(self):
        '''Shut down the work queue'''
        with self.shutdown_lock:
            self.shutdown_ = True
        with self.work_condition:
            self.work_condition.notifyAll()
