#!/usr/bin/env python

import utils
import datetime
import re, lxml.html, lxml.etree, StringIO 
import json
import logging

cuerpo = 'D'
base_url = "http://www.parlamento.gub.uy"

def run(options):
  cache = utils.flags().get('cache', False)
  force = not cache
  scrape(options)

def scrape(options):
  hoy = datetime.datetime.now().strftime('%d%m%Y')
  fecha  = options.get('fecha', hoy)
  integracion = options.get('integracion', 'D')
  tipoleg = options.get('tipoleg', 'Tit')
  orden = options.get('orden', 'Legislador')
  grafico = options.get('grafico', 's')

  query = "?Fecha=%s&Cuerpo=%s&Integracion=%s&TipoLeg=%s&Orden=%s&Grafico=%s" % (fecha,cuerpo,integracion,tipoleg,orden,grafico)
  url_to_scrape = "http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.asp%s" % query

  logging.info("Scrapeando informacion de diputados desde pagina del parlamento. \nURL: %s." % url_to_scrape)

  body = utils.download(url_to_scrape, 'legisladores/camara_%s_%s.html' % (cuerpo, hoy), options.get('force', False), options)
  doc = lxml.html.document_fromstring(body)

  tablas = doc.xpath("//table")
  rows = tablas[3].cssselect('tr td')

  diputados = []
  for row in rows:
      mail_base = row.xpath("a[starts-with(@href, 'mailto')]/@href")
      if mail_base:
          email = mail_base[0].split(':',1)[1]
      else:
          email = ''

      congress_people = {
        'nombre'   : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[1]),
        'apellido' : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[0]),
        'partido'  : format_word(row.xpath('br/following-sibling::text()')[1]),
        'email': email,
        'foto' : base_url+row.xpath('img/@src')[0],
        'departamento' : row.xpath('br/following-sibling::text()')[2]
      }
      diputados.append(congress_people)

  output_path = "data/diputados.json"

  utils.write(
    json.dumps(diputados, sort_keys=True, indent=2, default=utils.format_datetime, encoding="utf-8"), 
    output_path
  )

def format_word(nombre):
  return nombre.strip().lower().encode("utf-8")
