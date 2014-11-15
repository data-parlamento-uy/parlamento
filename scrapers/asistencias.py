#!/usr/bin/env python
# -*- coding: latin-1 -*-

import utils
import urllib
import urllib2
import re, lxml.html, lxml.etree, StringIO
import datetime
import json
import logging
from lxml.html.clean import clean_html, Cleaner
import time

base_url = "http://www.parlamento.gub.uy"

FECHA_INICIO_LEGISLATURA_ACTUAL = '15022010'
NRO_LEGISLATURA_ACTUAL          =  47

def run(options):
  cache = utils.flags().get('cache', False)
  force = not cache
  scrape(options)

def scrape(options):
  hoy = datetime.datetime.now().strftime('%d%m%Y')

  cuerpo = options.get('cuerpo', 'S')
  fecha_inicio = options.get('fechaini', FECHA_INICIO_LEGISLATURA_ACTUAL)
  fecha_fin = options.get('fechafin', hoy)

  query = '?Cuerpo=%s&Legistaltura=%s' % (cuerpo, NRO_LEGISLATURA_ACTUAL)
  url = base_url + '/gxemule/ConsAsistencia.asp' + query

  logging.info("Escrapeando informacion de asistencias desde la pagina del parlamento.\nURL: %s.\n" % url)

  # Generar sesion
  req_sess = urllib2.Request(url)
  response = urllib2.urlopen(req_sess)
  cookie = response.headers.get('Set-Cookie')

  # Setear parametros POST
  form_data = {
  	'FecDesde'    : fecha_inicio,
  	'FecHasta'    : fecha_fin,
  	'Cuerpo'      : cuerpo,
  	'Ini'         : fecha_inicio,
  	'Fin'         : fecha_fin,
  	'Legislatura' : NRO_LEGISLATURA_ACTUAL,
  	'Fechas'      : 'Seleccionado',
    'Asistencia'  : 'Legislador',
    'Orden'       : 'ASC'
  }

  # Ejecutar POST con cookie y parametros
  data = urllib.urlencode(form_data)
  req = urllib2.Request(url, data)
  req.add_header('cookie', cookie)

  response = urllib2.urlopen(req)
  the_page = response.read()

  # Guardar pagina
  filename = "cache/asistencias/camara_%s_%s-%s.html" % (cuerpo, fecha_inicio, fecha_fin)
  utils.write(the_page, filename)
  doc = lxml.html.document_fromstring(the_page)

  tabla_datos = doc.xpath('//table[@bordercolordark="#D1D6D5"]')[0]
  rows = tabla_datos.xpath('tr')

  info_asistencias = []

  first = True
  for row in rows:
    if first:
      first = False
    else:
      data = {}
      columnas = row.xpath('td')
      data['nombre'] = columnas[0].text_content()
      data['citaciones'] = columnas[1].text_content().strip()
      data['asistencias'] = columnas[2].text_content()
      data['faltas_con_aviso'] = columnas[4].text_content()
      data['faltas_sin_aviso'] = columnas[6].text_content()
      data['no_citado_por_licencia'] = columnas[8].text_content()
      data['no_citado_por_estar_ejerciendo_presidencia'] = columnas[9].text_content()

      info_asistencias.append(data)


  output_path = "data/asistencias_%s.json" % cuerpo
  utils.write(
    json.dumps(info_asistencias, sort_keys=True, indent=1, encoding='utf-8'),
    output_path
  )