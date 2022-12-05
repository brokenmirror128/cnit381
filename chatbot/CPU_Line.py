%matplotlib notebook

from matplotlib import pyplot as plt
from matplotlib import style
from matplotlib.animation import FuncAnimation
import time

class LiveLine:
  def __init__(self):
    self.x_date, self.y_data = [], []
    self.figure = plt.figure()
    self.figure.suptitle('CPU%', fontsize=18)
    self.line, = plt.plot(self.x_data, self.y_data, '--')
    plt.xlabel('Time(s)', fontsize=12)
    plt.ylabel('Percentage', fontsize=12)
    self.animation = FuncAnimation(self.figure, self.update, interval=1000)
    self.th = Thread(target=self.thread_f, daemon=True)
    self.th.start()
    
  def update(self, frame):
    self.line.set_data(self.x_data, self.y_data)
    self.figure.gca().relim()
    self.figure.gca().autoscale_view()
    return self.line,
  
  def show(self):
    plt.show()
    
  def thread_f(self):
    x=0
    while True:
      self.x_data.apped(x)
      x+=1
      self.y_data.append(get_cpu())
      time.sleep(1)
      
g = LiveLine()
g.show()
