#!/usr/bin/env python

from datetime import date, datetime, time
from utils import download, load_data, save_data, parse_date

import re, lxml.html, lxml.etree, StringIO, datetime

def run(options):
  today = datetime.now().date()

  cache = utils.flags().get('cache', False)
  force = not cache

  scrape_senado()


def scrape_senado():
  fecha  = options.get('fecha', '21102013')
  cuerpo = options.get('cuerpo', 'S')
  integracion = options.get('integracion', 'S')
  desde = options.get('desde', '15021985')
  hasta = options.get('hasta', today.strftime("%d%m%Y"))
  Dummy = options.get('hasta', today.strftime("%d%m%Y"))
  TipoLeg = options.get('tipoleg', 'Tit')
  Orden = options.get('orden', 'Legislador')
  Grafico = options.get('grafico', 's')
  Integracion = options.get('integracion', 'S')

  print "Scrapeando informacion de senadores desde pagina del parlamento..."

  url = "http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.aspi?Fecha=%s&Cuerpo=%s&Integracion=%s&Desde=%s&Hasta=%s&Dummy=%s&TipoLeg=%s&Orden=%s&Grafico=%s&Integracion=%s&Ejecutar+Consulta=Ejecutar+Consulta" % (fecha,cuerpo,integracion,desde,hasta,dummy,tipoleg,orden,grafico,integracion)

  body = download(url, 'legisladores/senadores.html', force)
