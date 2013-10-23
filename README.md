Un repositorio de dominio publico donde tener codigo para extraer datos desde el sitio web del parlamento uruguayo.

Inspirado en el trabajo que varias organizaciones estan haciendo en http://github.com/unitedstates/

*Configuracion del ambiente*

En linux hay que instalar los siguientes paquetes

    sudo apt-get install git python-virtualenv python-dev libxml2-dev libxslt1-dev

Se puede crear y activar una entorno virtual

    virtualenv uruguay
    source uruguay/bin/activate

Y luego instalar los paquetes (con entorno virtual o sin el)

    pip install -r requerimientos.txt

Para levantar los datos

  ./run <nombre-del-script> [--force] [otras opciones]


donde los scripts que tenemos hasta el momento son:

    * contactos-senadores


*Extraccion de datos de Legisladores*


*camara de senadores*

Extraemos la informacion desde la pagina http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.asp?Fecha=21102013&Cuerpo=S&Integracion=S&Desde=15021985&Hasta=21102013&Dummy=21102013&TipoLeg=Tit&Orden=Legislador&Grafico=s&Integracion=S&Ejecutar+Consulta=Ejecutar+Consulta

*camara de representantes*

Extraemos la informacion desde la pagina http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.asp?Fecha=21102013&Cuerpo=D&Integracion=S&Desde=15021985&Hasta=21102013&Dummy=21102013&TipoLeg=Tit&Orden=Legislador&Grafico=s&Integracion=S&Ejecutar+Consulta=Ejecutar+Consulta

Los campos para incluir en la consulta son:

Fecha=21102013
Cuerpo=
       S -> senadores
       D -> diputados
Integracion=S
Desde=15021985
Hasta=21102013
Dummy=21102013
TipoLeg=Tit
Orden=Legislador
Grafico=s
Integracion=S
Ejecutar+Consulta=Ejecutar+Consulta
