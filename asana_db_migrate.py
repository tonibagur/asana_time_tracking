import asana_db
from pprint import pprint
from api_flow import *

class ZODBMigrator(object):
    def __init__(self):
        self.db=asana_db.AsanaDB()

    def get_tracks(self):
        for x in self.db.root.tracks:
            yield {'task':x.task.id,
                   'user':x.employee.id,
                   'minutes':x.minutes,
                   'start_time':x.start_time.isoformat(),
                   'end_time':x.end_time.isoformat()
                   }


def migrate_db():
    #print [x for x in ZODBMigrator().get_tracks()]
    error_time_tracking=ListAcumulator()
    error_get_task=ListAcumulator()
    put_tasks=ListAcumulator()
    get_tasks=ListAcumulator()
    pre_tracks=ListAcumulator()
    post_tracks=ListAcumulator()
    bp=BreakPoint(error_time_tracking,error_get_task,pre_tracks,get_tasks,put_tasks,post_tracks)
    migrator=ZODBMigrator()
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    coneptum_asana=ConeptumAsanaAPI('','time_tracking',debug=True)
    coneptum_asana2=ConeptumAsanaAPI('','asana_db',debug=True)
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    ListProcessor(migrator,'get_tracks').out(
        ElementFilter(Ev("elem['task']==17065298387027")).out(
            Printer("+++Tracks"),
            pre_tracks,
            ElementProcessor(asana_api,'get_task',[Ev("elem['task']")],{}).out(
                Printer('----Task'),
                get_tasks,
                TxTask().out(
                    ElementProcessor(coneptum_asana2,'_asana_put',(Ev("'tasks/'+str(elem['id'])"),Ev("elem"))),
                    put_tasks,
                )
            ).error(error_get_task),
            post_tracks,
            ElementProcessor(coneptum_asana,'_asana_post',('time_tracking',Ev("elem"))).error(error_time_tracking,bp),
        )
    ).process()
    print "Errors time tracking", error_time_tracking.count()
    print "Detail", error_time_tracking.list


if __name__=='__main__':
    migrate_db()