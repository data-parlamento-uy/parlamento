#!/usr/bin/env python

import utils
import datetime
import re
import lxml.html, lxml.etree, StringIO
import json
import logging

base_url = "http://www.parlamento.gub.uy"
cuerpo = 'S'

def run(options):
  cache = utils.flags().get('cache', False)
  force = not cache
  scrape(options)

def scrape(options):
  hoy = datetime.datetime.now().strftime('%d%m%Y')
  fecha  = options.get('fecha', hoy)
  integracion = options.get('integracion', 'S')
  tipoleg = options.get('tipoleg', 'Tit')
  orden = options.get('orden', 'Legislador')
  grafico = options.get('grafico', 's')


  query = "?Fecha=%s&Cuerpo=%s&Integracion=%s&TipoLeg=%s&Orden=%s&Grafico=%s" % (fecha,cuerpo,integracion,tipoleg,orden,grafico)
  url_to_scrape = "http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.asp%s" % query

  logging.info("Scrapeando informacion de senadores desde pagina del parlamento.\nURL: %s.\n" % url_to_scrape)

  body = utils.download(url_to_scrape, 'legisladores/camara_%s_%s.html' % (cuerpo, hoy), options.get('force', False), options)
  doc = lxml.html.document_fromstring(body)

  tablas = doc.xpath("//table")
  rows = tablas[3].cssselect('tr td')

  senadores = [] # Un arreglo con todos los senadores
  presidente_de_la_camara = True # La primera fila no es identificable y tiene un campo mas (titulo) que queremos tomar
  for row in rows:
      if presidente_de_la_camara:
          congress_people = {
              'nombre'   : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[1]),
              'apellido' : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[0]),
              'titulo'   : row.xpath('br/following-sibling::text()')[2].strip().encode("utf-8"),
              'partido'  : format_word(row.xpath('br/following-sibling::text()')[3]),
              'email'    : row.xpath("a[starts-with(@href, 'mailto')]/@href")[0].split(':',1)[1],
              'foto'     : base_url+row.xpath('img/@src')[0]
          }
          presidente_de_la_camara = False
      else:
          congress_people = {
            'nombre'    : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[1]),
            'apellido'  : format_word(row.xpath('br/following-sibling::text()')[0].split(',')[0]),
            'partido  ' : format_word(row.xpath('br/following-sibling::text()')[1]),
            'email'     : row.xpath("a[starts-with(@href, 'mailto')]/@href")[0].split(':',1)[1],
            'foto'      : base_url+row.xpath('img/@src')[0]
          }
      senadores.append(congress_people)

  parlamento = {
      "fecha": hoy,
      "senadores": senadores
  }
  output_path = "data/senadores.json"

  utils.write(
    json.dumps(parlamento, sort_keys=True, indent=2, default=utils.format_datetime, encoding="utf-8"), 
    output_path
  )

def format_word(nombre):
  return nombre.strip().lower().encode("utf-8")
