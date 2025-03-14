# https://stackoverflow.com/a/78071937
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore


class BoundedThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, max_workers=5, max_task_size=5, *args, **kwargs):
        """等待队列有限的线程池. 任务数量超出上限时, submit将阻塞

        Args:
            max_workers (int): ThreadPoolExecutor最大工作线程数. 默认5
            max_task_size (int): 处于运行和等待状态的任务的最大数量. 默认5
        """
        if max_task_size < max_workers:
            raise ValueError(
                'max_task_size should be greater than or equal to max_workers'
            )
        if max_workers is not None:
            kwargs['max_workers'] = max_workers
        super().__init__(*args, **kwargs)
        self._semaphore = Semaphore(max_task_size)

    def submit(self, timeout=3600, *args, **kwargs):
        if self._semaphore.acquire(timeout=timeout):
            future = super().submit(*args, **kwargs)
            future.add_done_callback(lambda _: self._semaphore.release())
            return future
        else:
            raise TimeoutError('waiting for semaphore timeout')


# threadpool: BoundedThreadPoolExecutor
