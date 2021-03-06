
#from multiprocessing import Process
import RPi.GPIO as GPIO
import time
import MySQLdb
import datetime
from datetime import timedelta

buzz_pin=4
led_pin=17
not_pin=19
cam_pin=26
ativar=0
tempo_antigo = datetime.datetime.now()
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzz_pin,GPIO.OUT)
GPIO.setup(not_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(cam_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
con = MySQLdb.connect('127.0.0.1', 'root', 'watchdogs')
con.select_db('wdp')
start = time.time()
sql = con.cursor()
sql.execute('SELECT nome, pin FROM sensors')
#dicionario = {}

for row in sql.fetchall():
	if (row[0] == "janela1"):
		janela1 = int(row[1])
		print "Janela1 ->" + str(janela1)
	elif (row[0] == "janela2"):
	   	janela2 = int(row[1])
		print "Janela2 ->" + str(janela2)
	elif (row[0] == "janela3"):
	    	janela3 = int(row[1])
		print "Janela3 ->" + str(janela3)
	elif (row[0] == "sala1"):
	    	sala1 = int(row[1])
		print "Sala1 ->" + str(sala1)
	elif (row[0] == "quarto1"):
	    	quarto1 = int(row[1])
		print "Quarto1 ->" + str(quarto1)
	elif (row[0] == "quarto2"):
	    	quarto2 = int(row[1])
		print "Quarto2 ->" + str(quarto2)
	   
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
	con.commit()
	for row in sql.fetchall():
		if (int(row[1]) == 2 and ativar==0):
			GPIO.output(buzz_pin,GPIO.HIGH)
                        time.sleep(0.5)
                        GPIO.output(buzz_pin,GPIO.LOW)
                        time.sleep(0.5)
                        GPIO.output(buzz_pin,GPIO.HIGH)
                        time.sleep(0.5)
                        GPIO.output(buzz_pin,GPIO.LOW)
                        time.sleep(0.5)
                        GPIO.output(buzz_pin,GPIO.HIGH)
			ativar=1
			
def desativar():
	global ativar
	GPIO.output(buzz_pin,GPIO.LOW)
	ativar = 0
def inserir(idsensor,tipo):
	global con
	global sql
	global tempo_antigo
	sql.execute('SELECT MAX(id_historico) FROM  historico')
        con.commit()
        max=int(sql.fetchone()[0])
        max=max+1
        now=datetime.datetime.now()
        sql.execute("INSERT INTO historico(id_historico,id_sensor,tipo_ocorrencia,data_ocorrencia) VALUES (%s,%s,%s,%s)",(str(max),idsensor,tipo,now.strftime('%Y-%m-%d %H:%M:%S')))
        con.commit()
def notificacao(tipo):
	global con
        global sql
        sql.execute('SELECT MAX(id_not) FROM  notificacao')
        con.commit()
        max=int(sql.fetchone()[0] or 0)
        max=max+1
        now=datetime.datetime.now()
        sql.execute("INSERT INTO notificacao(id_not,tipo_not) VALUES (%s,%s)",(str(max),tipo+now.strftime('%Y-%m-%d %H:%M:%S')))
        con.commit()
def agendamento(tipo):
	global con
	global sql
	sql.execute('SELECT '+tipo+', situacao FROM  agendamento')
	con.commit()
	for data in sql.fetchall():
	  datas=datetime.datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S')
	  if datetime.datetime.now()>=datas-timedelta(weeks=0, days=0, hours=0, minutes=5, seconds=0) and tipo=='data_ativ'and int(data[1])==0:
	    print 'boa!'
	    time.sleep(0.1)
	    sql.execute('UPDATE agendamento SET situacao=2 where data_ativ=%s',(data[0]))
	    con.commit()
	    inserir(None,'Faltam menos de 5 minutos para o acionamento do alarme')
	   # notificacao('Faltam menos de 5 minutos para o acionamento do alarme, que ocorre em ')
	  if datetime.datetime.now()>=datas and tipo=='data_ativ' and int(data[1])!=1:
	    sql.execute('UPDATE sensors SET status=1 WHERE status=-1')
	    con.commit()
            sql.execute('UPDATE agendamento SET situacao=1 where data_ativ=%s',(data[0]))
            con.commit()
	    print 'passou'
	    inserir(None,'ativamento agendado')
	  if datetime.datetime.now()>=datas and tipo=='data_desativ':
	    sql.execute('UPDATE sensors SET status=-1')
	    con.commit()
	    inserir(None,'desativamento agendado')
	    sql.execute('DELETE FROM agendamento where data_desativ=%s',(data[0]))
	    print 'deu'
	    con.commit()

def sensores():
	sql = con.cursor()
	validar=0
	notific=0
	hist=0
	global ativar	
	while True:	
			if(GPIO.input(not_pin)):
			  inserir(None,'Sujeito estranho na porta')
			  #notificacao('Sujeito estranho na porta em ')
			  time.sleep(0.2)
			sql.execute('SELECT pin, status, id FROM sensors')
		        con.commit()
			agendamento('data_ativ')
			for row in sql.fetchall():
			   if GPIO.input(int(row[0])) and int(row[1]) ==1  or int(row[1])==2 and ativar==0 :
			      if int(row[1])!=2 and GPIO.input(int(row[0])):
			      	sql.execute('UPDATE sensors SET status=2 WHERE id=%s',(row[2]))
			      	con.commit() 
			      if ativar==0:
				time.sleep(0.1)
                                inserir(row[2],'disparo')
				time.sleep(0.1)
				#notificacao('O alarme foi disparado em ')
			      disparar()
			  # if GPIO.input(janela2) and int(row[1]) == 1:
			  #    sql.execute('UPDATE sensors SET status=2 WHERE status=1')
			  #    con.commit()   
			  #    disparar()
			  # if GPIO.input(janela3) and int(row[1]) == 1:
			  #    sql.execute('UPDATE sensors SET status=2 WHERE status=1')
			  #    con.commit()   
			  #    disparar()
			  # if GPIO.input(sala1) and int(row[1]) == 1:
			  #    sql.execute('UPDATE sensors SET status=2 WHERE status= 1')
			  #    con.commit()   
			  #    disparar()
			  # if GPIO.input(quarto1) and int(row[1]) == 1:
			  #    sql.execute('UPDATE sensors SET status=2 WHERE status = 1')
			  #    con.commit()   
			  #    disparar()
			  # if GPIO.input(quarto2) and int(row[1]) == 1:
			  #    sql.execute('UPDATE sensors SET status=2 WHERE status = 1')
			  #    con.commit()   
			  #    disparar()
				  
			# if GPIO.input(janela1) | GPIO.input(janela2) | GPIO.input(janela3) | GPIO.input(sala1) | GPIO.input(quarto1) | GPIO.input(quarto2):
				# sql.execute('UPDATE sensors SET status=2 WHERE status = 1')
				# con.commit()   
				# disparar()
			sql.execute('SELECT nome, status,id FROM sensors')
			con.commit()
			for row in sql.fetchall():
			  if GPIO.input(cam_pin)and int(row[1])!=-1 and hist==0:
			     time.sleep(0.1)
			     hist=1
			     sql.execute('UPDATE sensors SET status=-1')
                             con.commit()
			     time.sleep(0.1)
			     inserir(None,'Alarme desativado pela camera')
			     time.sleep(0.1)
			hist=0
			agendamento('data_desativ')
			sql.execute('SELECT id, status FROM sensors')
			con.commit()
			for row in sql.fetchall():
				if (int(row[1]) == 0 and ativar==1):
					desativar()
				if (int(row[1]) == 0 and hist==0):
					inserir(None,'Alarme desativado')
					hist=1
					#notificacao(' O alarme foi desativado em ')
				        sql.execute('UPDATE sensors SET status=-1 WHERE status = 0')
                             	        con.commit()
			hist=0	

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
