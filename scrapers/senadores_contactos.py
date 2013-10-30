#!/usr/bin/env python

from datetime import date, datetime, time
#from utils import download, load_data, save_data, parse_date
import utils

import re, lxml.html, lxml.etree, StringIO, datetime, json

def run(options):
#  today = datetime.now().date()
    cache = utils.flags().get('cache', False)
    force = not cache
    scrape_senado(options)

def scrape_senado(options):
    today = datetime.datetime.now().strftime('%Y%m%d')
    fecha  = options.get('fecha', today)
    cuerpo = options.get('cuerpo', 'S')
    integracion = options.get('integracion', 'S')
    tipoleg = options.get('tipoleg', 'Tit')
    orden = options.get('orden', 'Legislador')
    grafico = options.get('grafico', 's')
    integracion = options.get('integracion', 'S')

    print "Scrapeando informacion de senadores desde pagina del parlamento..."
    url = "http://www.parlamento.gub.uy/GxEmule/IntcpoGrafico.asp?Fecha=%s&Cuerpo=%s&Integracion=%s&TipoLeg=%s&Orden=%s&Grafico=%s" % (fecha,cuerpo,integracion,tipoleg,orden,grafico)
    body = utils.download(url, 'legisladores/camara_%s_%s.html' % (cuerpo, today), options.get('force', False), options)
    doc = lxml.html.document_fromstring(body)
    tablas = doc.xpath("//table")
    rows = tablas[3].cssselect('tr td')
    congress_arr = []
    i = 1
    for row in rows:
        print i
        #image row.xpath('img/@src')[0]
        if (i == 1 and cuerpo == 'S'):
            congress_people = {
                'name': row.xpath('br/following-sibling::text()')[0],
                'desc': row.xpath('br/following-sibling::text()')[2],
                'party': row.xpath('br/following-sibling::text()')[3],
                'email': row.xpath("a[starts-with(@href, 'mailto')]/@href")[0].split(':',1)[1]
            }
        else:
            congress_people = {
              'name': row.xpath('br/following-sibling::text()')[0],
              'party': row.xpath('br/following-sibling::text()')[1],
              'email': row.xpath("a[starts-with(@href, 'mailto')]/@href")[0].split(':',1)[1]
            }
            if (cuerpo == 'D'):
                congress_people['zone'] = row.xpath('br/following-sibling::text()')[1]
        i+=1
        congress_arr.append(congress_people)
    file = "data/camara_%s_legisladores.json" % cuerpo
    utils.write(json.dumps(congress_arr),file)