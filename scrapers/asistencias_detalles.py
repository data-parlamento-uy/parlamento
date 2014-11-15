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
  url = base_url + '/gxemule/ConsAsistenciaBrief.asp' + query

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
  	'Fechas'      : 'Seleccionado'
  }

  # Ejecutar POST con cookie y parametros
  data = urllib.urlencode(form_data)
  req = urllib2.Request(url, data)
  req.add_header('cookie', cookie)

  response = urllib2.urlopen(req)
  the_page = response.read()

  # Guardar pagina
  filename = "cache/asistencias_por_sesion/camara_%s_%s-%s.html" % (cuerpo, fecha_inicio, fecha_fin)
  utils.write(the_page, filename)
  doc = lxml.html.document_fromstring(the_page)

  info_sesiones = doc.xpath('//center/a/b')
  info_asistencias = doc.xpath('//div[@align="justify"]')

  index = 0
  sesiones = []

  while index < len(info_sesiones):
    data = {}

    info_sesion = info_sesiones[index].xpath('text()')
    data['nro_sesion'] = re.sub(r'\D', "", info_sesion[0])
    data['fecha'] = info_sesion[1]

    data['asistencias'] = []
    data['faltas_con_aviso'] = []
    data['faltas_sin_aviso'] = []
    data['faltas_por_licencia'] = []
    data['notas'] = []

    notes_keys = {}
    scrape_asistencias(data, info_asistencias[index], notes_keys)

    sesiones.append(data)
    index +=1

  output_path = "data/asistencias_detalles_%s.json" % cuerpo
  utils.write(
    json.dumps(sesiones, sort_keys=True, indent=1, encoding='utf-8'),
    output_path
  )


def scrape_asistencias(data, div, notes_keys):
  cleaner = Cleaner(remove_tags=['b'])
  texts = cleaner.clean_html(div).xpath('text()')
  for text in texts:
    text = text.strip()
    if re.match('Asisten los', text):
      data['asistencias'] = scrape_nombres(text, notes_keys)
    elif re.match('Falta(n|) con aviso', text):
      data['faltas_con_aviso'] = scrape_nombres(text, notes_keys)
    elif re.match('Falta(n|) sin aviso', text):
      data['faltas_sin_aviso'] = scrape_nombres(text, notes_keys)
    elif re.match('No citados por licencia', text):
      data['faltas_por_licencia'] += scrape_nombres(text, notes_keys)
    elif re.match('En ejercicio de la Presidencia de la', text):
      data['faltas_por_licencia'] += scrape_nombres(text, notes_keys)
    elif len(text) > 1:
      if re.search(r'\((\d)\)', text):
        data['notas'].append(add_note(text, notes_keys))
      else:
        data['asistencias'] = scrape_nombres(text, notes_keys)


def scrape_nombres(text, notes_keys):
  text_parts = text.split(':')
  text = text_parts[len(text_parts)-1]
  names = text.replace(' y ', ', ').split(',')
  return [clean_name(name, notes_keys) for name in names]

def add_note(text, notes_keys):
  m = re.search(r'\((\d)\)', text)
  note_ref = m.group(1)

  note_text = re.sub(r'\(\d\)', '', text)
  note_text = note_text.strip()

  return {notes_keys[note_ref]: note_text}


def clean_name(text, notes_keys):
  text = text.strip()
  m = re.search(r'\((\d)\)', text)

  text = re.sub(r'\.$', '', text)
  text = re.sub(r'\(\d\)$', '', text)
  text = text.strip()

  if m:
    notes_keys[m.group(1)] = text

  return text
