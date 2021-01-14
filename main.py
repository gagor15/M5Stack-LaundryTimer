import time
from m5stack import *


class Sounds:

  def __init__(self, volume=2):
    speaker.volume(volume)
    speaker.tone(freq=1000, duration=200)

  def beeps(self, n_beeps, beep_time, pause_time):
    for i in range(n_beeps):
      speaker.tone(freq=1000, duration=50)
      time.sleep(beep_time)
      speaker.tone(freq=1, duration=50)
      time.sleep(pause_time)
    # speaker.tone(freq=1, duration=50)


class Timer:

  def __init__(self):
    # Variables
    self.timer_end = None
    self.last_time_printed = None
    self.timer_running = False

    # Sounds
    self.sounds = Sounds(volume=0.2)

    # Set font
    lcd.font(lcd.FONT_7seg)
    lcd.attrib7seg(20, 20, lcd.WHITE, lcd.BLACK)
    lcd.clear()

    # Button setup
    buttonA.wasReleased(self.on_A_released)
    buttonB.wasReleased(self.on_B_released)

    # Initialise variables
    self.stop(silent=True)

  def stop(self, silent=False):
    self.timer_end = time.time()
    self.timer_running = False
    self.print_time_left(0)
    if not silent:
      pass
      # self.sounds.beeps(3, 0.5, 1.0)

  def start(self, t_sec):
    self.timer_end = time.time() + t_sec
    self.timer_running = True

  def print_time_left(self, t_sec):
    t_sec = int(t_sec)
    mins = int(t_sec / 60)
    secs = t_sec % 60
    time_left_str = "{:02d}:{:02d}".format(mins, secs)
    lcd.print(time_left_str, lcd.CENTER, 64)
    self.last_time_printed = t_sec

  def on_A_released(self):
    self.start(5)

  def on_B_released(self):
    self.start(2*60)

  def run(self):
    # Loop
    while True:
      # Sample time
      t_current = time.time()

      # Check timer and print
      if self.timer_running:
        t_diff = int(self.timer_end - t_current)
        if t_diff <= 0:
          self.stop()
        elif t_diff != self.last_time_printed:
          self.print_time_left(t_diff)
      else:
        time.sleep(0.01)


if __name__ == "__main__":
  timer = Timer()
  timer.run()
