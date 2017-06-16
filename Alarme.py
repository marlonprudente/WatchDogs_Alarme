
from multiprocessing import Process
import RPi.GPIO as GPIO
import time
import MySQLdb

buzz_pin=4
led_pin=14

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_pin, GPIO.OUT)
GPIO.setup(buzz_pin,GPIO.OUT)
con = MySQLdb.connect('127.0.0.1', 'root', 'watchdogs')
con.select_db('wdp')
start = time.time()
sql = con.cursor()
sql.execute('SELECT nome, pin FROM sensors')

for row in sql.fetchall():
   if (row[0] == "janela1"):
      janela1 = row[1]
	#elif (row[0] == "janela2"):
	#   janela2 = row[1]
	#elif (row[0] == "janela3"):
	#   janela3 = row[1]
	#elif (row[0] == "sala1"):
	#   sala1 = row[1]
	#elif (row[0] == "quarto1"):
	#   quarto1 = row[1]
	#elif (row[0] == "quarto2"):
	#   quarto2 = row[1]
	   
GPIO.setup(janela1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(janela2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(janela3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(sala1, GPIO.IN)
#GPIO.setup(quarto1, GPIO.IN)
#GPIO.setup(quarto2, GPIO.IN)

# def Ativar():
	# sql = con.cursor()
	# sql.execute('SELECT nome, status FROM sensors')
	
   # for row in sql.fetchall():
	  # status_sensor = row[0] + row[1]
      # if (status_sensor < 0):
         # sql.execute('UPDATE sensors SET status=1 WHERE status=-1')
	     # return True
      # elif(status_sensor == len(row)):
         # return True
      # else:
         # return False

# def Desativar():
	# sql = con.cursor()
	# sql.execute('SELECT nome, status FROM sensors')
	
   # for row in sql.fetchall():
	# status_sensor += row[1]
   # if (status_sensor == len(row)):
      # sql.execute('UPDATE sensors SET status=-1 WHERE status=1')
	  # return True
   # elif(status_sensor < 0):
      # return True
   # else:
      # return False	

def disparar():
	sql = con.cursor()
	sql.execute('SELECT nome, status FROM sensors')
    global start	
	while True:	
      for row in sql.fetchall():
	     if (row[1] == 2):
		    Process(target=led).start()
    	    Process(target=buzzer).start()

def sensores():
	sql = con.cursor()
	sql.execute('SELECT nome, status FROM sensors')
    global start
	while True:	
      for row in sql.fetchall():
	     if GPIO.input(janela1 || janela2 || janela3 || sala1 || quarto1 || quarto2):
		    sql.execute('UPDATE sensors SET status=2 WHERE status=1')

		    

	   

def led():
    global start
    while True:
        GPIO.output(led_pin,GPIO.HIGH)
        time.sleep(3)
        GPIO.output(led_pin,GPIO.LOW)
        time.sleep(3)
def buzzer():
    global start
    while True:
        GPIO.output(buzz_pin,GPIO.HIGH)
        time.sleep(3)
        GPIO.output(buzz_pin,GPIO.LOW)
        time.sleep(3)






try:
  while True:
      Process(target=sensores).start()
	  Process(target=disparar).start()
except KeyboardInterrupt:
  print "voce usou Ctrl+C!"
finally:
  GPIO.cleanup()
