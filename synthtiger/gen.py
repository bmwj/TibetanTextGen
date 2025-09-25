"""
SynthTIGER
Copyright (c) 2021-present NAVER Corp.
MIT license
"""

import itertools
import os
import random
import sys
import traceback
from multiprocessing import Process, Queue

import imgaug
import numpy as np
import yaml

# 尝试导入 tqdm，如果没有则提供一个简单的替代
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # 简单的进度条替代类
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
            self.iterable = iterable or range(total) if total else []
            self.total = total or len(self.iterable) if hasattr(self.iterable, '__len__') else 0
            self.desc = desc or "Progress"
            self.n = 0
            
        def __iter__(self):
            for item in self.iterable:
                yield item
                self.update(1)
                
        def update(self, n=1):
            self.n += n
            if self.total > 0:
                percent = (self.n / self.total) * 100
                print(f"\r{self.desc}: {self.n}/{self.total} ({percent:.1f}%)", end="", flush=True)
                
        def close(self):
            if self.total > 0:
                print()  # 换行
                
        def set_postfix(self, **kwargs):
            pass  # 简单实现，不显示额外信息


def read_template(path, name, config=None):
    path = os.path.abspath(path)
    root = os.path.dirname(path)
    module = os.path.splitext(os.path.basename(path))[0]
    sys.path.append(root)
    template = getattr(__import__(module), name)(config)
    sys.path.remove(root)
    del sys.modules[module]
    return template


def read_config(path):
    with open(path, "r", encoding="utf-8") as fp:
        config = yaml.load(fp, Loader=yaml.SafeLoader)
    return config


def generator(
    path, name, config=None, count=None, worker=0, seed=None, retry=True, verbose=False, progress=False
):
    counter = range(count) if count is not None else itertools.count()
    tasks = _task_generator(seed)
    
    # 创建进度条（如果需要且有count）
    pbar = None
    if progress and count is not None:
        pbar = tqdm(
            total=count,
            desc="🎨 生成图像",
            unit="张",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )

    if worker > 0:
        task_queue = Queue(maxsize=worker)
        data_queue = Queue(maxsize=worker)
        pre_count = min(worker, count) if count is not None else worker
        post_count = count - pre_count if count is not None else None

        for _ in range(worker):
            _run(_worker, (path, name, config, task_queue, data_queue, retry, verbose))
        for _ in range(pre_count):
            task_queue.put(next(tasks))

        for idx in counter:
            task_idx, data = data_queue.get()
            if post_count is None or idx < post_count:
                task_queue.put(next(tasks))
            
            # 更新进度条
            if pbar is not None:
                pbar.update(1)
                pbar.set_postfix({"任务": task_idx})
                
            yield task_idx, data
    else:
        template = read_template(path, name, config)

        for idx in counter:
            task_idx, task_seed = next(tasks)
            data = _generate(template, task_seed, retry, verbose)
            
            # 更新进度条
            if pbar is not None:
                pbar.update(1)
                success_status = "✅" if data is not None else "❌"
                pbar.set_postfix({"状态": success_status, "任务": task_idx})
                
            yield task_idx, data
    
    # 关闭进度条
    if pbar is not None:
        pbar.close()


def get_global_random_states():
    states = {
        "random": random.getstate(),
        "numpy": np.random.get_state(),
        "imgaug": imgaug.random.get_global_rng().state,
    }
    return states


def set_global_random_states(states):
    random.setstate(states["random"])
    np.random.set_state(states["numpy"])
    imgaug.random.get_global_rng().state = states["imgaug"]


def set_global_random_seed(seed=None):
    random.seed(seed)
    np.random.set_state(np.random.RandomState(np.random.MT19937(seed)).get_state())
    imgaug.random.seed(seed)


def _run(func, args):
    proc = Process(target=func, args=args)
    proc.daemon = True
    proc.start()
    return proc


def _task_generator(seed):
    random_generator = random.Random(seed)
    task_idx = -1

    while True:
        task_idx += 1
        task_seed = random_generator.getrandbits(128)
        yield task_idx, task_seed


def _worker(path, name, config, task_queue, data_queue, retry, verbose):
    template = read_template(path, name, config)

    while True:
        task_idx, task_seed = task_queue.get()
        data = _generate(template, task_seed, retry, verbose)
        data_queue.put((task_idx, data))


def _generate(template, seed, retry, verbose):
    states = get_global_random_states()
    set_global_random_seed(seed)
    data = None

    while True:
        try:
            data = template.generate()
        except:
            if verbose:
                print(f"{traceback.format_exc()}")
            if retry:
                continue
        break

    set_global_random_states(states)
    return data