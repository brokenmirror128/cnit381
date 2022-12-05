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


class Livepie:
  def __init__(self):
    self.data = [30,70]
    self.figure, self.pie_chart = plt.subplots()
    self.figure.suptitle('Memory Usage%', fontsize=18)
    self.labels = 'Used', 'Free'
    self.explod = (0, 0.1)
    self.colors = ("Magenta", "Cyan")
    self.pie_chart.axis('equal')
    self.animation = FuncAnimation(self.figure, self.update, interval = 1000)
    self.th = Thread(target=self.thread_f, daemon=True)
    self.th.start()
    
  def update(self, frame):
    self.pie_chart.pie(self.data, explode=self.explode,labels = self.labels, colors = self.colors,
                       autopct='%1.1f%%', shadow=True, startangle=90)
    self.figure.gca().relim()
    self.figure.gca().autoscale_view()
    return self.pie_chart,
  
  def show(self):
    print('showing chart!')
    
  def thread_f(self):
    while True:
      self.data = get_mem()
      plt.pause(0.001)
      plt.draw()
      time.sleep(1)
      
g = LivePie()
g.show()
