#!/usr/bin/env python
# -*- coding: latin-1 -*-

from datetime import date, datetime, time
#from utils import download, load_data, save_data, parse_date
import utils
import urllib
import urllib2
import re, lxml.html, lxml.etree, StringIO, datetime, json

#options = {}
def run(options):
	cache = utils.flags().get('cache', False)
	force = not cache
	if (options.get('data', 'commissions') == 'commissions'):
		scrape_comissions(options)


def scrape_comissions(options):
	#options D o S
	chamber = options.get('cuerpo', 'S')
	#options Act o Tit
	legs = options.get('tipoleg', 'Act')
	today = datetime.datetime.now().strftime('%d%m%Y')
	date_value  = options.get('fecha', today)
	url = 'http://www.parlamento.gub.uy/GxEmule/intcomind.asp?Cuerpo=%s' % chamber
	#generamos la sesion
	req_sess = urllib2.Request(url)
	response = urllib2.urlopen(req_sess)
	cookie = response.headers.get('Set-Cookie')
	form_data = {
		'Fecha' : date_value,
		'Cuerpo' : chamber,
		'Integracion' : chamber,
		'TipoLeg' : legs,
		'Desde' : '01062001',
		'Hasta' : today,
		'Dummy' : today
	}
	data = urllib.urlencode(form_data)
	req = urllib2.Request(url, data)
	req.add_header('cookie', cookie)
	#ejecutamos el post
	response = urllib2.urlopen(req)
	the_page = response.read()
	#Guardo la pagina, este metodo habria que ponerlo en utils ya que hay muchos posts
	utils.write(the_page, 'cache/comisiones/comisiones.html')
	doc = lxml.html.document_fromstring(the_page)
	#Scrapeamos las comisiones por fila para sacar headers
	tabla = doc.xpath("//table")[4].xpath("tr")
	commissions = []
	for row in tabla:
		if (row.getchildren()[0].tag == 'th'):
			cat = row.text_content().strip()
		else:
			#Nos quedamos con la primera parte del nombre separado por la coma
			name = row.text_content().strip().split(',', 1)[0]
			commission = {
				'name' : name,
				'type' : cat,
				'chamber' : chamber,
			}
			href = row.cssselect('a')[0].get('href')
			commission = commision_integration(href, name, chamber, options)
			print commission
			#commission['members'] = specs[0]
			#commission['secretary'] = specs[1]
			#commission['meeting'] = specs[2]
			#commission['email'] = specs[3]
			commissions.append(commission)
	file = "data/comisiones_%s_%s.json" % (chamber, today)
	utils.write(json.dumps(commissions),file)

def commision_integration(href_comp, name, chamber, options):
	base_url = 'http://www.parlamento.gub.uy/GxEmule/'
	url = base_url + href_comp
	body = utils.download(url, 'comisiones/'+name+'.html', options.get('force', False), options)
	doc = lxml.html.document_fromstring(body)
	rows = doc.xpath("//div[contains(@style,'border:0px solid #006699')]/div")[0].xpath("//div[contains(@style,'width:750px')]/div")
	divs = rows[0].cssselect('div')
	result = {}
	pre_res = []
	i = 1
	top = 0
	start = False
	for div in divs:
		if (i == top):
			result[cat] = pre_res
			break
		elif div.text_content().strip() == 'Miembros':
			cat = 'members'
			start = True
		elif div.text_content().strip() == 'Secretaría':
			#appendamos los miembros
			result[cat] = pre_res
			pre_res = []
			cat = 'secretary'
		elif div.text_content().strip() == 'Reuniones':
			#appendamos la secretaria
			result[cat] = pre_res
			cat = 'meetings'
			pre_res = []
			top = i + 2
		elif start:
			#store data
			data = {
				'text' : div.text_content().strip(),
				'type' : cat,
				'chamber' : chamber,
			}
			pre_res.append(data)
		i+=1		
		email_exists = doc.xpath("//a[starts-with(@href, 'mailto')]/@href")
		if email_exists:
			email = email_exists[0].split(':',1)[1]
		else:
			email = 'none'
		data = {
				'text' : email,
				'type' : 'email',
				'chamber' : chamber,
			}
		result['email'] = data
	return result
