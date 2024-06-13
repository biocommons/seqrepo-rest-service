#!/usr/bin/env python3

"""
SeqRepo REST Service load testing. Used for validating concurrency / file descriptor bug fixes.

Also useful for testing response performance of the seqrepo-rest-service program. Prints the
average request completion rate (requests/second) at the end.

Uses multiprocessing.Process to create parallel workers (count=`-n`) sending requests to a
SeqRepo REST Service endpoint (`-u`). Sends `-m` requests with different values. Uses `-s` local
seqrepo directory to get viable input values from and monitors the number of open files using lsof.

If running the seqrepo rest service through Docker, the lsof monitoring will only work if the seqrepo
directory the REST service uses is mounted as a local volume in the `docker run`. It cannot be on
a persistent docker volume or copied in at runtime because lsof will not see the open files.

Example docker run for server, where a local seqrepo directory exists at /usr/local/share/seqrepo/latest:
```
docker run -it --rm \
    -p 5000:5000 \
    -v /usr/local/share/seqrepo/latest:/seqrepo/latest \
    biocommons/seqrepo-rest-service:0.2.2 \
    seqrepo-rest-service /seqrepo/latest
```

Example command (20 worker processes, 500 requests, monitoring /usr/local/share/seqrepo/latest):
```
python load-test.py -n 20 -s /usr/local/share/seqrepo/latest -m 500 -u 'http://localhost:5000/seqrepo'
```

A successful run will exit successfully, with no exceptions in the load-test.py process or in
the seqrepo rest service process. And the open file count logged by load-test.py will not increase
continuously but rather stabilize at a relatively low level on the order of tens of files.
"""


import argparse
import pathlib
import random
import subprocess
import logging
import time
import sys
import queue
import multiprocessing  # as multiprocessing
from typing import TextIO

from biocommons.seqrepo import SeqRepo
from biocommons.seqrepo.dataproxy import SeqRepoRESTDataProxy

_logger = logging.getLogger()


def log(log_queue: multiprocessing.Queue, line: str):
    log_queue.put(line + "\n")


def lsof_count(dirname: str) -> int:
    lsof_cmd = [
        "bash", "-c",
        f"lsof +D {dirname} | wc -l"]
    lsof_p = subprocess.Popen(
        lsof_cmd,
        stdout=subprocess.PIPE)
    (stdout, _) = lsof_p.communicate()
    stdout = stdout.decode("utf-8").strip()
    return int(stdout)


class LsofWorker(multiprocessing.Process):
    def __init__(self, dirname, check_interval=5):
        """
        check_interval: seconds between open file checks
        """
        self.dirname = dirname
        self.check_interval = check_interval
        super().__init__()

    def run(self):
        try:
            while True:
                ct = lsof_count(self.dirname)
                print(f"{self.dirname} open file count {ct}", flush=True)
                time.sleep(self.check_interval)
        except InterruptedError:
            pass


class MPWorker(multiprocessing.Process):
    close_sentinel_value = -1

    def __init__(self, q: multiprocessing.Queue, seqrepo_uri: str):
        self.q = q
        self.seqrepo_uri = seqrepo_uri
        self.seqrepo_dataproxy = SeqRepoRESTDataProxy(seqrepo_uri)
        self.n = 0
        self.query_bound_start = 0
        self.query_bound_end = 5
        super().__init__()

    def run(self):
        while True:
            try:
                ac = self.q.get(False)
                if ac == MPWorker.close_sentinel_value:
                    print(f"{self}: Done; processed {self.n} accessions", flush=True)
                    break
                self.seqrepo_dataproxy.get_sequence(
                    ac, self.query_bound_start, self.query_bound_end)
                self.n += 1
            except queue.Empty:
                pass


def queue_filler_target(q, acs, n_workers):
    """
    Callable target for queue filler. Necessary because multiprocess.Queue
    uses pipes with a buffer limit that is relatively low. Background process
    ensures queue keeps getting rest of input values, plus close sentinels.
    """
    for ac in acs:
        q.put(ac)
    for _ in range(n_workers):
        q.put(MPWorker.close_sentinel_value)
    print("Done filling input queue", flush=True)


class StdOutPipeWorker(multiprocessing.Process):
    """
    Used for synchronized logging between main and sub processes
    """

    def __init__(self, stdout_queue: multiprocessing.Queue, ostream: TextIO = None):
        self.stdout_queue = stdout_queue
        self.ostream = ostream if ostream else sys.stdout
        self.stopped = False
        super().__init__()

    def run(self):
        while not self.stopped:
            try:
                val = self.stdout_queue.get(timeout=0.5)
                print(val, file=self.ostream, end="")
            except queue.Empty:
                pass

    def stop(self):
        self.stopped = True


def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-n", "--num-workers", type=int, default=1)
    ap.add_argument("-s", "--seqrepo-path", type=pathlib.Path, required=True,
                    help="Local SeqRepo instance to get input values from, and to monitor open file count in")
    ap.add_argument("-u", "--seqrepo-rest-uri", type=str, default="http://localhost:5000/seqrepo")
    ap.add_argument("-m", "--max-accessions", type=int, required=True)
    ap.add_argument("-f", "--fd-cache-size", type=int, default=0)
    opts = ap.parse_args(argv)
    return opts


def main(argv):
    opts = parse_args(argv)

    sr = SeqRepo(root_dir=opts.seqrepo_path, fd_cache_size=opts.fd_cache_size)

    acs = set(a["alias"] for a in sr.aliases.find_aliases(namespace="RefSeq", alias="NM_%"))
    acs = random.sample(sorted(acs), opts.max_accessions or len(acs))

    input_queue = multiprocessing.Queue()

    # log_queue = multiprocessing.Queue(maxsize=10000)
    # log_worker = StdOutPipeWorker(log_queue, sys.stdout)
    # log_worker.start()

    t_filler = multiprocessing.Process(
        target=queue_filler_target, args=(input_queue, acs, opts.num_workers))
    t_filler.start()

    workers = []
    for _ in range(opts.num_workers):
        workers.append(MPWorker(input_queue, opts.seqrepo_rest_uri))

    lsof_p = None
    print("Starting lsof process")
    lsof_p = LsofWorker(opts.seqrepo_path, 1)
    lsof_p.start()

    # Sleep briefly to let input queue get ahead
    time.sleep(1)
    print("Finished initialization")

    time_start = time.time()
    print("Starting workers")
    for w in workers:
        w.start()

    for w in workers:
        w.join()

    time_end = time.time()
    time_diff = time_end - time_start

    if lsof_p:
        lsof_p.terminate()

    print(f"Retrieved {len(acs)} seq in {time_diff} seconds ({len(acs)/time_diff} seq/sec)")

    # log_worker.stop()
    # log_worker.join()


if __name__ == "__main__":
    import coloredlogs
    coloredlogs.install(level="INFO")
    main(argv=sys.argv[1:])
