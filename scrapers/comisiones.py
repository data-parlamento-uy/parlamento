#!/usr/bin/env python
# -*- coding: latin-1 -*-

import utils
import urllib
import urllib2
import re, lxml.html, lxml.etree, StringIO
import datetime
import json
import logging

base_url = "http://www.parlamento.gub.uy"

def run(options):
  cache = utils.flags().get('cache', False)
  force = not cache
  scrape(options)

def scrape(options):
  # opciones D o S. Por defecto Senado
  cuerpo = options.get('cuerpo', 'S')
  # opciones Act o Tit. Por defecto Activo
  legs = options.get('tipoleg', 'Act')
  
  hoy = datetime.datetime.now().strftime('%d%m%Y')
  fecha = options.get('fecha', hoy)
  
  desde = options.get('desde', '01062001')
  hasta = options.get('hasta', hoy)
  
  query = '?Cuerpo=%s' % cuerpo
  url = base_url + '/GxEmule/intcomind.asp' + query
  
  logging.info("Escrapeando informacion de comisiones desde la pagina del parlamento.\nURL: %s.\n" % url)

  # generamos la sesion
  req_sess = urllib2.Request(url)
  response = urllib2.urlopen(req_sess)
  
  cookie = response.headers.get('Set-Cookie')
  form_data = {
  	'Fecha'       : fecha,
  	'Cuerpo'      : cuerpo,
  	'Integracion' : cuerpo,
  	'TipoLeg'     : legs,
  	'Desde'       : desde,
  	'Hasta'       : hasta,
  	'Dummy'       : hoy
  }

  data = urllib.urlencode(form_data)

  req = urllib2.Request(url, data)
  req.add_header('cookie', cookie)
  
  # Ejecutamos el post
  response = urllib2.urlopen(req)
  the_page = response.read()
  
  # Guardo la pagina
  utils.write(the_page, 'cache/comisiones/comisiones.html')
  doc = lxml.html.document_fromstring(the_page)

  # Escrapeamos las comisiones por fila para sacar headers
  tabla = doc.xpath("//table")[4].xpath("tr")

  comisiones = []
  for row in tabla:
    if (row.getchildren()[0].tag == 'th'):
      cat = row.text_content().strip()
    else:
     # Nos quedamos con la primera parte del nombre separado por la coma
      name = row.text_content().strip().split(',', 1)[0]
      comision = {
     	'nombre' : name,
     	'categoria' : cat,
     	'cuerpo' : cuerpo,
      }
      href = row.cssselect('a')[0].get('href')
      # Buscamos tambien la integracion
      comision['integracion'] = integracion(href, name, cuerpo, options)
      comisiones.append(comision)

  output_path = "data/comisiones.json"
  utils.write(
    json.dumps(comisiones, sort_keys=True, indent=1, default=utils.format_datetime ,encoding='utf-8'), 
    output_path
  )
  
def integracion(href_comp, name, cuerpo, options):
  url = base_url + '/GxEmule/' + href_comp

  body = utils.download(url, 'comisiones/'+name+'.html', options.get('force', False), options)
  doc = lxml.html.document_fromstring(body)
  rows = doc.xpath("//div[contains(@style,'border:0px solid #006699')]/div")[0].xpath("//div[contains(@style,'width:750px')]/div")
  divs = rows[0].cssselect('div')

  result = {}
  pre_res = []
  lineas = 1
  top = 0
  start = False
  for div in divs:
    if (lineas == top):
    	result[cat] = pre_res
    	break
    elif div.text_content().strip() == 'Miembros':
    	cat = 'miembros'
    	start = True
    elif div.text_content().strip() == u'Secretaría':
    	# agregamos los miembros
	cat = 'miembros'
    	result[cat] = pre_res
    	pre_res = []
    	cat = 'secretaria'
    elif div.text_content().strip() == 'Reuniones':
    	# agregamos la secretaria
	cat = 'secretaria'
    	result[cat] = pre_res
    	cat = 'reuniones'
    	pre_res = []
    	top = lineas + 2
    elif start:
    	#store data
    	data = {
    		'text' : div.text_content().strip(),
    		'tipo' : cat,
    		'cuerpo' : cuerpo,
    	}
    	pre_res.append(data)
    lineas += 1		
    email_exists = doc.xpath("//a[starts-with(@href, 'mailto')]/@href")
    if email_exists:
    	email = email_exists[0].split(':',1)[1]
    else:
    	email = 'none'
    data = {
      		'correo' : email,
    		'cuerpo' : cuerpo,
    	}
    result['email'] = data
  return result
