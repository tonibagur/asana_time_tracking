from asana import asana
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def mark_as_invoiced():
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    myspaces = asana_api.list_workspaces()
    coneptum_space = [s for s in myspaces if s['name']=='Coneptum'][0]
    #print coneptum_space
    tags= asana_api.get_tags(coneptum_space['id'])
    to_invoice_tag=[t for t in tags if t['name']=='to_invoice'][0]
    invoiced_tag=[t for t in tags if t['name']=='invoiced'][0]
    #print to_invoice_tag
    to_invoice_tasks=asana_api.get_tag_tasks(to_invoice_tag['id'])
    for t in to_invoice_tasks:
        if t['name']!='Fluxe Movil':
        	print t
        	#asana_api.add_tag_task(t['id'],invoiced_tag['id'])
        	asana_api.rm_tag_task(t['id'],to_invoice_tag['id'])

mark_as_invoiced()