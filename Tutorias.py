from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from lxml import html
from bs4 import Comment
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client

import sys
import os
import csv
from pathlib import Path
######### from html_table_extractor.extractor import Extractor

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
Chrome="chromedriver/chromedriver.exe"
browser = webdriver
session_requests = requests.session()

SEMESTRE=""
SubAreaCode="" ### Codigo del subarea docente
username=""
password=""
path=""


def Guardar_CSV(Nombre, cabecera, datos):
	csvsalida = open(Nombre, 'w')
	salida = csv.writer(csvsalida, delimiter=';',lineterminator="\n")
	salida.writerow(cabecera)
	salida.writerows(datos)
	del salida
	csvsalida.close()

def Leer_CSV(Nombre):
	if Path(Nombre).is_file():
		lista=[]
		with open(Nombre, newline='') as csvfile:
				 reader = csv.reader(csvfile, delimiter=';')
				 header=next(reader)
				 for row in reader:
						 lista.append(row)
		return header, lista
	else: print (Nombre + " No existe")

def leer_seeting():
	global SEMESTRE
	global SubAreaCode
	global username
	global password
	global path
	(set_head,setting)=Leer_CSV("Settings.csv")
	(SEMESTRE,SubAreaCode,username,password,path) = setting[0]

def SESSION():
	#### SESSION #####
	global browser
	global username
	global password
	global option
	global Chrome
	browser = webdriver.Chrome(executable_path="chromedriver/chromedriver.exe", chrome_options=option)
	URL_sesion="http://cv.uoc.edu/UOC/rac/tutor.html"
	browser.get(URL_sesion)
	WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='img-responsive']")))
	un = browser.find_element_by_id("username") #username form field
	pw = browser.find_element_by_id("password") #password form field
	un.send_keys(username)
	pw.send_keys(password)
	submitButton = browser.find_element_by_xpath("//button[@class='btn btn-default btn-block']")
	submitButton.click() 
	WebDriverWait(browser, 120).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='img--thumbnail']")))
	SESS= browser.current_url.replace(URL_sesion,"").replace("?s=","")
	### MODO TUTOR
	browser.get("http://cv.uoc.edu/rb/inici/grid?s="+SESS)
	WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='userprofile__thumb']")))
	browser.find_element_by_xpath("//select[@id='profile']/option[@value='UOC-TUTOR_PG-pg-b']").click()
	print()
	print()
	return SESS

def PLANES(SESSION):
	### PLANES de Estudio tutorizados###
	URL_Planes="https://cv.uoc.edu/tren/trenacc?modul=GAT_EXP.ESTUDTUTOR%2Fpuet.puet&s="+SESSION
	rPlanes = uReq(URL_Planes)
	Planes_soup = soup(rPlanes.read(), "html.parser")
	rPlanes.close()
	
	## El código html aparece dentro del código javascript, por lo que es posible tratarlo como html, sin embargo, las variables que buscamos aparecen precedidas por el string  "i_codplan="
	Init=0
	Planes=[]
	### Numero de ocurencias del string "i_codplan="
	for I in range(Planes_soup.text.count("i_codplan=")):
			### Busca desde la ultima ocurrencia, la siguiente
			Init=Planes_soup.text.find("i_codplan=",Init)
			Init=Init+10
			### Alimenta Lista de planes
			Plan=[]
			Plan.append(Planes_soup.text[Init:Init+4])
			Planes.append(Plan)
	del Plan
	del Init
	del Planes_soup
	return Planes



def ALUMNOS(SESSION, Plan):
	### ALUMNOS TUTORIZADOS ###
	URL_Alumnos="https://cv.uoc.edu/tren/trenacc?modul=GAT_EXP.ESTUDTUTOR/puet.alumnes_tutor&i_nip=465122&i_codplan="+Plan+"&s="+SESSION+"&i_any_academic="+SEMESTRE
	global browser
	browser.get(URL_Alumnos)
	Alumnos=[]
	Alumn_soup = soup(browser.page_source, "html.parser")
	if len(Alumn_soup.find_all('table')) > 4:
		rows = Alumn_soup.find_all('table')[4].find('tbody').find_all('tr')
		for row in rows:
			if rows.index(row) > 1:
				### Ficha_code;Semestre;Plan_code;
				Alumn=row.find_all('td')[0].find('a').attrs['href'].replace("javascript:doNovaFitxaEst('","").replace("');","").replace("','",";") +";"
				### Datos Basicos Ficha 
				IDP=Alumn.split(sep=';')[0]
				URL_Ficha="https://cv.uoc.edu/tren/trenacc?modul=ADN.MOSTRAR_FICHA&entidad_gestora=UOC&tipo_identificador=IDP&tipo_ficha=FICPERS&codi_identificador="+IDP+"&s="+SESSION
				rFicha = uReq(URL_Ficha)
				Ficha_soup = soup(rFicha.read(), "html.parser")
				### Alt_email
				Alumn=Alumn + Ficha_soup.find("table", id="DADES_BASIQUES").find_all('td')[17].text +";"
				### email;Ap_Nom
				Alumn=Alumn+row.find_all('td')[1].find('a').attrs['href'].replace("javascript:sendMail('","").replace("@uoc.edu');","")+";"+ row.find_all('td')[1].find('a').text +";"
				### Ingreso
				Alumn=Alumn+row.find_all('td')[2].text  +";"
				### Nuevo
				if len(row.find_all('img')) > 1: Alumn=Alumn+"1"
				Datos_Alumn=Alumn.split(sep=';')
				Alumnos.append(Datos_Alumn)
		rFicha.close()
	return Alumnos



def ASIGNATURAS(SESSION, IDP, anyAcademic): 
	### ASIGNATURAS ###
	URL_Asignaturas="https://cv.uoc.edu/webapps/rac/viewSecretaria.action?s="+SESSION+"&modul=GAT_EXP.NOTESAVAL/rac.rac&tipus=1&idp="+IDP+"&anyAcademic="+anyAcademic
	global browser
	browser.get(URL_Asignaturas)
	User_id= browser.current_url.replace("http://cv.uoc.edu/UOC/rac/listAulasEstudiant.html?userId=","").replace("&s="+SESSION+"&anyAcademic="+anyAcademic,"")
	AlumnosAsignaturas=[]
	### espera a que carge la pagina
	WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='img--thumbnail']")))
	AlAsign_soup = soup(browser.page_source, "html.parser")
	for AA in AlAsign_soup.findAll("div", {"class": "row bg-grey-light padding-custom-list-aulas p-2x assignatura-border"}):
			### Ficha_code;User_Id;Semestre;Asign_Nom
			Datos_AlumnAsign=IDP +";"+User_id+";"+anyAcademic+ ";"+ AA.find("a", {"class": "a__underline"}).text.replace("<b>","").replace("</b>","")
			### Asig_Code;Aula  --- URL_Asign http://cv.uoc.edu/UOC/rac/ estudiante.html?anyAcademic=20181&codiTercers=B2.578&numAula=2&userId=1198656;
			Datos_AlumnAsign=Datos_AlumnAsign+";"+ AA.find("a", {"class": "a__underline"}).attrs['href'].replace("estudiante.html?anyAcademic="+anyAcademic,"").replace("&codiTercers=","").replace("numAula=","").replace("&userId="+User_id,"").replace('&',";")
			### Asign_Prof
			if len(AA.find("a", {"class": "a__underline h5 text-small"}).text.split(sep=','))< 4:
				Datos_AlumnAsign=Datos_AlumnAsign+";"+AA.find("a", {"class": "a__underline h5 text-small"}).text
			else: 
				Datos_AlumnAsign=Datos_AlumnAsign+";Varios"
			#### Solo las asignaturas del Area B2 = Busines Intelligence
			if Datos_AlumnAsign.split(sep=';')[4].split(sep='.')[0] == SubAreaCode:
				AlumnosAsignaturas.append(Datos_AlumnAsign.split(sep=';'))
	return AlumnosAsignaturas



def PECS(SESSION,User_Id,Semestre,Asig_Code,Aula):
	### PECS ###
	URL_PEC="http://cv.uoc.edu/UOC/rac/estudiante.html?s="+ SESSION +"&anyAcademic="+Semestre+"&codiTercers="+Asig_Code+"&numAula="+Aula+"&userId="+User_Id
	global browser
	browser.get(URL_PEC)
	### espera a que carge la pagina
	WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='img--thumbnail']")))
	PEC_soup = soup(browser.page_source, "html.parser")
	ID=[]
	### Semester;Asig_code;Aula;userId
	ID.append(User_Id)
	ID.append(Semestre)
	ID.append(Asig_Code)
	ID.append(Aula)
	pecs=[]
	for row in PEC_soup.find_all('tr',{"class": "subtitle-comment-student-desp doc level1 ruler--bottom ruler--thin odd"}):
			cleanrow=row.find_all('p')
			Datos_pec=[]
			Datos_pec.extend(ID)
			#### PEC;PEC_Fecha;PEC_Entrega;PEC_Nota;PEC_Publicacion
			Datos_pec.append(cleanrow[0].text)
			Datos_pec.append(cleanrow[2].text)
			Datos_pec.append(cleanrow[1].text)
			Datos_pec.append(row.find('strong').text)
			Datos_pec.append(cleanrow[3].text)
			pecs.append(Datos_pec)
	return pecs


def Ultima_Conexion(SESSION,IDP):
	URL_Conex="https://cv.uoc.edu/tren/trenacc?modul=ADN.MOSTRAR_FICHA&entidad_gestora=UOC&tipo_identificador=IDP&tipo_ficha=FCAMPUS&codi_identificador="+IDP+"&s="+SESSION
	rConex = uReq(URL_Conex)
	Conex_soup = soup(rConex.read(), "html.parser")
	rConex.close()
	last_conex = ''
	if len(Conex_soup.find_all("table", id="3542")) == 1:
		conexiones= Conex_soup.find("table", id="3542").find_all('td')
		last_conex=IDP +';'
		last_conex=last_conex + (conexiones[4].text) +';'
		last_conex=last_conex+(conexiones[6].text)
	else:
		last_conex=IDP +';;'
	
	return last_conex.split(sep=';')


def backspace(n):
		print('\r', end='')                     # use '\r' to go back



def MENU_TODO():
	global browser
	global path
	leer_seeting()
	session = SESSION()
	
	planes=PLANES(session)
	print("Procesando PLANES:   100%")
	out_filename =path+ "PLANES.csv"
	###### header of csv file to be written
	headers = ["PLAN"]
	Guardar_CSV(out_filename, headers, planes)
	print()
	
	alumnos=[]
	tot=len(planes)
	cuenta=0
	for plan in planes:
		cuenta +=1
		backspace(len(str(round(100*cuenta/tot)) +"%"))
		print("Procesando ALUMNOS:   "+  str(round(100*cuenta/tot)) +"%", end='')
		alumnos = alumnos + ALUMNOS(session,plan[0])
	
	# name the output file to write to local disk
	out_filename = path+"ALUMNOS.csv"
	# header of csv file to be written
	headers = "Ficha_code;Semestre;Plan_code;Alt_email;email;Ap_Nom;Ingreso;Nuevo"
	Guardar_CSV(out_filename, headers.split(sep=';'), alumnos)
	print()
	print()
	
	conexiones=[]
	tot=len(alumnos)
	cuenta=0
	for alumno in alumnos:
		cuenta +=1
		backspace(len(str(round(100*cuenta/tot)) +"%"))
		print("Procesando CONEXIONES:   "+  str(round(100*cuenta/tot)) +"%", end='')
		conexiones.append(Ultima_Conexion(session,alumno[0]))  ###IDP
	
	# name the output file to write to local disk
	out_filename=path+"CONEXIONES.csv"
	# header of csv file to be written
	headers = "Ficha_code;Ultima_Conex;Ultima_Accion"
	# opens file, and writes
	Guardar_CSV(out_filename, headers.split(sep=';'), conexiones)
	print()
	print()
	
	asignaturas=[]
	tot=len(alumnos)
	cuenta=0
	for alumno in alumnos:
		cuenta +=1
		backspace(len(str(round(100*cuenta/tot)) +"%"))
		print("Procesando ASIGNATURAS:   "+  str(round(100*cuenta/tot)) +"%", end='')
		asignaturas=asignaturas + ASIGNATURAS(session, alumno[0], SEMESTRE)
	
	# name the output file to write to local disk
	out_filename=path+"ASIGNATURAS.csv"
	# header of csv file to be written
	headers = "Ficha_code;User_Id;Semestre;Asign_Nom;Asig_Code;Aula;Asign_Prof"
	# opens file, and writes
	Guardar_CSV(out_filename, headers.split(sep=';'), asignaturas)
	print()
	print()
	
	pecs=[]
	tot=len(asignaturas)
	cuenta=0
	for asig in asignaturas:
		cuenta +=1
		backspace(len(str(round(100*cuenta/tot)) +"%"))
		print("Procesando PECs:   "+  str(round(100*cuenta/tot)) +"%", end='')
		###							(SESSION, User_Id, Semestre,Asig_Code ,Aula)
		pecs=pecs + PECS(session, asig[1], asig[2], asig[4], asig[5])
	
	# name the output file to write to local disk
	out_filename=path+"PECS.csv"
	# header of csv file to be written
	headers = "User_Id;Semestre;Asig_Code;Aula;PEC;PEC_Fecha;PEC_Entrega;PEC_Nota;PEC_Publicacion"
	# opens file, and writes
	Guardar_CSV(out_filename, headers.split(sep=';'), pecs)
	print()
	print()
	browser.quit()

def MENU_UPDATE():
	global path
	global browser
	leer_seeting()
	session = SESSION()
	
	conexiones=[]
	# name the  file to read/write to local disk
	filename=path + "ALUMNOS.csv"
	# opens file, and reads to a header an body lists
	if Path(filename).is_file():
		(alumn_head,alumnos)=Leer_CSV(filename)
		###headers = "Ficha_code;Semestre;Plan_code;Alt_email;email;Ap_Nom;Ingreso;Nuevo"
		tot=len(alumnos)
		cuenta=0
		for alumno in alumnos:
			cuenta +=1
			backspace(len(str(round(100*cuenta/tot)) +"%"))
			print("Procesando CONEXIONES:   "+  str(round(100*cuenta/tot)) +"%", end='')
			conexiones.append(Ultima_Conexion(session,alumno[0]))  ###IDP
		# name the output file to write to local disk
		out_filename=path+"CONEXIONES.csv"
		# header of csv file to be written
		headers = "Ficha_code;Ultima_Conex;Ultima_Accion"
		# opens file, and writes
		Guardar_CSV(out_filename, headers.split(sep=';'), conexiones)
	else: 
		main("NO EXISTE: "+filename)
	print()
	print()
	
	pecs=[]
	# name the  file to read/write to local disk
	filename=path + "ASIGNATURAS.csv"
	# opens file, and reads to a header an body lists
	if Path(filename).is_file():
		(asig_head,asignaturas)=Leer_CSV(filename)
		####		headers = "Ficha_code;User_Id;Semestre;Asign_Nom;Asig_Code;Aula;Asign_Prof"
		tot=len(asignaturas)
		cuenta=0
		for asig in asignaturas:
			cuenta +=1
			backspace(len(str(round(100*cuenta/tot)) +"%"))
			print("Procesando PECs:   "+  str(round(100*cuenta/tot)) +"%", end='')
			###							(SESSION, User_Id, Semestre,Asig_Code ,Aula)
			pecs=pecs + PECS(session, asig[1], asig[2], asig[4], asig[5])
		# opens file, and writes
		out_filename=path + "PECs.csv"
		Guardar_CSV(out_filename, asig_head, pecs)
		browser.quit()
	else: 
		main("NO EXISTE: "+filename)
		browser.quit()
	print()
	print()


def menu(txt):
	os.system('cls')
	print(txt)
	print()
	print("Pulse 1, para actualizar PECs y Conexiones")
	print("Pulse 2, para actualizar TODO")
	print("Pulse 3, para actualizar SETTINGs")
	print("Pulse 4, para SALIR")
	print('')
	return  input("Su seleccion: ")

def input_setting():
	filename="Settings.csv"
	head="SEMESTRE;SubAreaCode;username;password;Path"
	settings=[]
	sett=[]
	sett.append(input("Introduce Semestre: "))
	sett.append(input("Introduce Subarea Code: ")) ### Codigo del subarea docente
	sett.append(input("Introduce username: "))
	sett.append(input("Introduce password: "))
	path=(input("Introduce Directorio de Salida (terminado en \): "))
	if Path(path).is_dir(): sett.append.path
	else: main (path + " No existe, crea ruta o cambia el Path en settings")
	settings.append(sett)
	# opens file, and writes
	Guardar_CSV(filename, head.split(sep=';'), settings)

def main(txt):
	opcion=menu(txt)
	print('')
	if opcion=="1": #PEC
		MENU_UPDATE()
	elif opcion=="2": # TODO
		MENU_TODO()
	elif opcion=="3": #Settings
		input_setting()
		main('')
	elif opcion=="4": #Salir
		global browser
		browser.quit()
		##breakmain
		####import sys  sys.exit()
	else: main('')

###SEMESTRE="20181"
###SubAreaCode="B2" ### Codigo del subarea docente
###username="******"
###password="******"
main('')


