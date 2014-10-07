from asana import asana
import asana_db
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def loop_time_tracking():
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    myspaces = asana_api.list_workspaces()
    coneptum_space = [s for s in myspaces if s['name']=='Coneptum'][0]
    #print coneptum_space
    tags= asana_api.get_tags(coneptum_space['id'])
    running_tag=[t for t in tags if t['name']=='running'][0]
    #print running_tag
    running_tasks=asana_api.get_tag_tasks(running_tag['id'])

    db=asana_db.AsanaDB()
    for t in running_tasks:
        tsk=asana_api.get_task(t['id'])
        print t['id'],t['name'],tsk['completed'],(tsk['assignee']['name'] if tsk['assignee'] else '<NO ASSIGNAT>')
        if tsk['assignee']:
            e=db.create_or_get_employee(tsk['assignee'])
            t2=db.create_or_get_task(tsk)
            t2.time_track(e)
        if tsk['completed'] or '[Duplicate]' in tsk['name']:
            print "Removing tag running from:",tsk['name']
            asana_api.rm_tag_task(t['id'],running_tag['id'])

    db.commit()

    print '----------------------TIME TRACKING:-------------------'
    for tr in db.get_tracks():
        print tr
    db.close()

while True:
    loop_time_tracking()
    time.sleep(4*60)

