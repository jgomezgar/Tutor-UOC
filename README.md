# Tutor-UOC
## Web Scraping to extract useful data for UOC Tutors about their alumns.

Extrae información útil para un tutor UOC acerca de sus alumnos:

Para ejecutar el script es necesario instalar la siguientes bibliotecas:
```
pip install selenium
pip install requests
pip install lxml
pip install beautifulsoup4
```
Adicionalmente es necesario el Driver para Chrome de Selenium:
```
https://sites.google.com/a/chromium.org/chromedriver/downloads
```
## USO
Al ejecutar el script Tutorias.py se obtiene el siguiente menu:

```

Pulse 1, para actualizar PECs y Conexiones
Pulse 2, para actualizar TODO
Pulse 3, para actualizar SETTINGs
Pulse 4, para SALIR

Su seleccion:

```

La opción 1, actualiza la informacion semanal acerca del alumno:
* Última conexión al campus.
* Fechas de Entrega y Calificaciones de sus PEC.
    
La opción 2, carga toda la estructura de datos necesaria:

  - **Planes** de estudio en los que colabora el Tutor.
  - **Alumnos** tutorizados bajo cada Plan.
  - **Asignaturas** de cada alumno del semestre.
  - **Última conexión** al Campus.
  - **PECs** de las asignaturas del semestre.
  
La opción 3, permite actualizar la configuracion:
* Semestre
* Subarea : código del plan general.
* Usuario.
* Password.
* Path: ruta donde guardar los ficheros generados.

## Para el primer uso, es necesario 1º Configurar "SETTINGs" y 2º cargar "TODO"
