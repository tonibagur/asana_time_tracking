import persistent
import transaction
import ZODB
import ZODB.FileStorage
import BTrees.OOBTree
import datetime

class AsanaDB(object):
    def __init__(self,db_path='asana_db.fs'):
        self.db = ZODB.DB(ZODB.FileStorage.FileStorage(db_path))
        self.root = self.db.open().root()
        if not hasattr(self.root,'tasks'):
            self.root.tasks=BTrees.OOBTree.BTree()
        if not hasattr(self.root,'employees'):
            self.root.employees=BTrees.OOBTree.BTree()
        if not hasattr(self.root,'tracks'):
            self.root.tracks=persistent.list.PersistentList()


    def close(self):
        self.db.close()

    def get_tracks(self):
        return self.root.tracks

    def create_or_get_task(self,tsk_data):
        t=None
        if tsk_data['id'] in self.root.tasks:
            t=self.root.tasks[tsk_data['id']]
            t.data=tsk_data
            t.update_data()
        else:
            t=Task(tsk_data,self.root.tracks)
            self.root.tasks[tsk_data['id']]=t
        return t

    def create_or_get_employee(self,emp_data):
        e=None
        if emp_data['id'] in self.root.employees:
            e=self.root.employees[emp_data['id']]
            e.data=emp_data
            e.update_data()
        else:
            e=Employee(emp_data)
            self.root.employees[emp_data['id']]=e
        return e

    def commit(self):
        transaction.commit()



class Task(persistent.Persistent):
    def __init__(self,data,all_tracks):
        self.data=data
        self.id=self.data['id']
        self.update_data()
        self.time_tracks=persistent.list.PersistentList()
        self.all_tracks=all_tracks

    def update_data(self):
        self.name=self.data['name']
    
    def time_track(self,employee,minutes=5):
        if len(self.time_tracks)>0 and self.time_tracks[-1].employee==employee and \
          (datetime.datetime.now() - self.time_tracks[-1].end_time).total_seconds()<(minutes*60):
            self.time_tracks[-1].add_track(minutes)
        else:
            t=TimeTrack(self,employee,datetime.datetime.now(),minutes)
            self.time_tracks.append(t) 
            self.all_tracks.append(t)

    def __str__(self):
        return "TSK:" + self.name

class Employee(persistent.Persistent):
    def __init__(self,data):
        self.data=data
        self.id=data['id']
        self.update_data()

    def update_data(self):
        self.name=self.data['name']

    def __str__(self):
        return "EMP:" + self.name


class TimeTrack(persistent.Persistent):
    def __init__(self,task,employee,start_time,minutes):
        self.task=task
        self.employee=employee
        self.start_time=start_time
        self.minutes=minutes
        self.end_time=self.start_time+datetime.timedelta(minutes=minutes)

    def __str__(self):
        return str(self.task) + " " +str(self.employee) + "MINUTES: " + str(self.minutes) + "START:" + str(self.start_time) + " END:" + str(self.end_time)

    def add_track(self,minutes):
        new_time=datetime.datetime.now()
        self.minutes+= (new_time - self.end_time).total_seconds()/60.
        self.end_time=new_time

