
from multiprocessing import Process
import RPi.GPIO as GPIO
import time
import MySQLdb

buzz_pin=4
led_pin=14
ativar=0
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(buzz_pin,GPIO.OUT)
con = MySQLdb.connect('127.0.0.1', 'root', 'watchdogs')
con.select_db('wdp')
start = time.time()
sql = con.cursor()
sql.execute('SELECT nome, pin FROM sensors')
dicionario = {}

for row in sql.fetchall():
	if (row[0] == "janela1"):
		janela1 = int(row[1])
		print "Janela1 ->" + janela1
	elif (row[0] == "janela2"):
	    janela2 = int(row[1])
		print "Janela2 ->" + janela1
	elif (row[0] == "janela3"):
	    janela3 = int(row[1])
		print "Janela3 ->" + janela1
	elif (row[0] == "sala1"):
	    sala1 = int(row[1])
		print "Sala1 ->" + janela1
	elif (row[0] == "quarto1"):
	    quarto1 = int(row[1])
		print "Quarto1 ->" + janela1
	elif (row[0] == "quarto2"):
	    quarto2 = int(row[1])
		print "Quarto2 ->" + janela1
	   
GPIO.setup(janela1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(janela2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(janela3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sala1, GPIO.IN)
GPIO.setup(quarto1, GPIO.IN)
GPIO.setup(quarto2, GPIO.IN)	

def disparar():
	global ativar
	sql = con.cursor()
	sql.execute('SELECT nome, status FROM sensors')
	for row in sql.fetchall():
		if (int(row[1]) == 2 and ativar==0):
			GPIO.output(buzz_pin,GPIO.HIGH)
			GPIO.output(led_pin,GPIO.HIGH)
			ativar=1
			

def sensores():
	sql = con.cursor()
	while True:	
			if GPIO.input(janela1 | janela2 | janela3 | sala1 | quarto1 | quarto2):
				sql.execute('UPDATE sensors SET status=2')
				con.commit()   
				disparar()

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
	GPIO.output(buzz_pin,GPIO.LOW)
	sql.execute('UPDATE sensors SET status=-1')
	con.commit()
	sensores()
	
except KeyboardInterrupt:
  print "voce usou Ctrl+C!"
finally:
  GPIO.cleanup()
