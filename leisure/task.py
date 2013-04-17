import os
import time
from collections import defaultdict

from .path import ensure_dir
import leisure


class Task(object):
  def __init__(self, id, job, input, mode):
    self.id = id
    self.job = job
    self.input = input
    self.mode = mode
    self.persisted_output = []
    self.output_file_name = None
    self.output_file = None
    self.host ="localhost"
    self.callbacks = defaultdict(list)

  def on(self, event, callback, *args):
    self.callbacks[event].append((callback, args))

  def fire(self, event):
    for callback, args in self.callbacks[event]:
      callback(*args)

  def done(self):
    if self.output_file:
      self.output_file.close()

    self.fire('done')

  def info(self):
    path = self.job.job_dir
    return dict(
      host       = self.host,
      disco_data = os.path.join(path, "data"),
      ddfs_data  = os.path.join(path, "ddfs"),
      master     = "http://localhost:8989",
      taskid     = self.id,
      jobfile    = self.job.jobfile_path, 
      mode       = self.mode, 
      jobname    = self.job.name, 
      disco_port = 8989,
      put_port   = 8990
    )

  @property
  def job_dir(self):
    return self.job.job_dir

  @property
  def worker_path(self):
    return self.job.worker_path

  def add_output(self, path, type, label):
    if self.output_file is None:
      self.new_output_file()
    self.output_file.write(self.format_output_line(path, type, label))


  def new_output_file(self):
    self.output_file_name = os.path.join(self.job_dir, self.results_filename())
    ensure_dir(self.output_file_name)
    self.output_file = open(self.output_file_name, 'w')


  def results_filename(self):
    time_stamp = int(time.time() * 1000)
    return os.path.join('.disco', "{}-{}-{:d}.results".format(
      self.mode, 
      self.id, 
      time_stamp
    ))

  def results(self):
    if self.output_file_name:
      local_results = self.local_results(self.output_file_name)
    else:
      local_results = None
    return local_results, self.persisted_output

  def local_results(self, file_name):
    return "dir://{}/{}".format(
      self.host,
      self.url_path(os.path.relpath(file_name, self.job_dir))
    )


  def format_output_line(self, local_path, type, label="0"):
    return "{} {}://{}/{}\n".format(label, type, self.host, self.url_path(local_path))


  def url_path(self, local_path):
    prefix = leisure.disco.job_url(self.host, self.job.name)
    return os.path.join(prefix, local_path)




