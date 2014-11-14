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
      # Buscamos tambien la integracion, email e informacion de reuniones
      agregar_informacion_extra(href, name, cuerpo, comision, options)
      comisiones.append(comision)

  output_path = "data/comisiones_%s.json" % cuerpo
  utils.write(
    json.dumps(comisiones, sort_keys=True, indent=1, default=utils.format_datetime ,encoding='utf-8'), 
    output_path
  )
  
def agregar_informacion_extra(href_comp, name, cuerpo, comision_data, options):
  print name
  url = base_url + '/GxEmule/' + href_comp

  body = utils.download(url, 'comisiones/'+name+'.html', options.get('force', False), options)
  doc = lxml.html.document_fromstring(body)
  rows = doc.xpath("//div[contains(@style,'border:0px solid #006699')]/div")[0].xpath("//div[contains(@style,'width:750px')]/div")

  divs = rows[0].xpath('div')
  categoria = ''
  comision_data['miembros'] = []
  comision_data['secretaria'] = []

  for div in divs:
    text = div.text_content().strip()
    if len(text) > 1:
      if re.match('Usuario:', text):
        break
      if text == 'Miembros':
        categoria = 'miembros'
      elif re.match('Secretar', text):
        categoria = 'secretaria'
      elif text == 'Reuniones':
        categoria = 'reuniones'
      elif re.match('Correo Elect', text):
        categoria = 'email'
      else:
        if categoria == 'miembros':
          comision_data['miembros'].append(text)
        elif categoria == 'secretaria':
          comision_data['secretaria'].append(text)
        elif categoria == 'reuniones':
          comision_data['reuniones'] = text
        elif categoria == 'email':
          comision_data['email'] = text
          break

