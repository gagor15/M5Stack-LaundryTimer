import time
import random
import os
import uos
import wave
from m5stack import lcd, buttonC, buttonB, buttonA
from machine import I2S


i2s = I2S(  mode = I2S.MODE_MASTER | I2S.MODE_TX | I2S.MODE_DAC_BUILT_IN,
            rate = 16000,
            bits = 16,
            channel_format = I2S.CHANNEL_ONLY_RIGHT,
            data_format = I2S.FORMAT_I2S_MSB)


def play_random_file(directory, volume=100):
  # Mount SD
  os.mountsd()

  # Get random file
  files = os.listdir(directory)
  rand_idx = random.randint(0, len(files)-1)
  fname = directory + '/' + files[rand_idx]

  # Open file and setup I2S
  wav = wave.open(fname)
  i2s.set_dac_mode(I2S.DAC_RIGHT_EN)
  i2s.sample_rate(wav.getframerate())
  i2s.bits(wav.getsampwidth() * 8)
  i2s.nchannels(wav.getnchannels()) 
  i2s.volume(volume)

  # Play file
  while True:
    data = wav.readframes(1024)
    if len(data) > 0:
      i2s.write(data)
      print('.', end='')
    else:
      wav.close()
      break
    if buttonC.isPressed():
      wav.close()
      break;
  
  # Stop I2S
  i2s.stop()
  i2s.set_dac_mode(I2S.DAC_DISABLE)  # Get rid of the speaker noise

  # Unmount SD because lcd interfers with it (both are on SPI)
  os.umountsd()


class Timer:

  def __init__(self, timer_A, timer_B):
    # Parameters
    self.timer_A = timer_A
    self.timer_B = timer_B

    # Variables
    self.timer_end = None
    self.last_time_printed = 0
    self.timer_running = False
    self.languages = []
    self.language_idx = 0
    self.language_dir = None
    self.pause = False

    # Set font
    self.set_timer_font()
    lcd.clear()

    # Button setup
    buttonA.wasReleased(self.on_A_released)
    buttonB.wasReleased(self.on_B_released)
    buttonC.wasReleased(self.on_C_released)

    # Initialise variables
    self.timer_end = time.time()
    self.timer_running = False
    self.print_time_left(0)

    # Read info from SD Card. Mount and unmount because it interfers with lcd SPI
    os.mountsd()
    self.languages = os.listdir('/sd')
    self.language_dir = '/sd/' + self.languages[self.language_idx]
    os.umountsd()
    self.print_language()

  def set_brightness(self, val): # From 0 to 100
    lcd.setBrightness(val)

  def set_timer_font(self):
    lcd.font(lcd.FONT_7seg)
    lcd.attrib7seg(20, 20, lcd.WHITE, lcd.BLACK)

  def print_language(self):
    lcd.clear()
    lcd.font(lcd.FONT_DejaVu24)
    lcd.print(self.languages[self.language_idx], 232, lcd.BOTTOM)
    self.set_timer_font()
    self.print_time_left(self.last_time_printed)

  def stop(self):
    self.timer_end = time.time()
    self.timer_running = False
    self.print_time_left(0)
    play_random_file(self.language_dir)
    
  def start(self, t_sec):
    play_random_file(self.language_dir)
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
    self.start(self.timer_A)

  def on_B_released(self):
    self.start(self.timer_B)

  def on_C_released(self):
    # Switch language directory
    self.language_idx = self.language_idx + 1
    if self.language_idx >= len(self.languages):
      self.language_idx = 0
    self.language_dir = '/sd/' + self.languages[self.language_idx]

    # Print language
    self.print_language()

    # Play language sample
    play_random_file(self.language_dir)

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
  timer = Timer(timer_A=25*60, timer_B=55*60)
  timer.run()


