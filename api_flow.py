from asana import asana
from coneptum_asana import ConeptumAsanaAPI
import traceback

class FlowElement(object):
    def __init__(self,connector=None,method=None,connector_largs=[],connector_kwargs={}):
        self.connector=connector
        self.connector_kwargs=connector_kwargs
        self.connector_largs=connector_largs
        self.method=method
        if type(self)!=NullProcessor:
            self.out_objects=[NullProcessor()]
            self.error_objects=[NullProcessor()]
    def compute_args(self,elem={}):
        new_largs=[x for x in self.connector_largs]
        new_kwargs=self.connector_kwargs.copy()
        for i,e in enumerate(new_largs):
            if type(e)==Ev:
                new_largs[i]=e.evaluate(elem)
        for k,v in new_kwargs.iteritems():
            if type(v)==Ev:
                new_kwargs[k]=v.evaluate(elem)
        return new_largs,new_kwargs
    def out(self,*out_objects):
        self.out_objects=out_objects
        return self
    def error(self,*error_objects):
        self.error_objects=error_objects
        return self

    def out_elem(self,e):
        for o in self.out_objects:
            o.process(e)
    def error_elem(self,e):
        for o in self.error_objects:
            o.process(e)

class NullProcessor(FlowElement):
    def process(self,elem={}):
        return

class ListProcessor(FlowElement):
    def process(self,elem={}):
        largs,kwargs=self.compute_args(elem)
        for x in getattr(self.connector,self.method)(*largs,**kwargs):
            self.out_elem(x)

class ElementProcessor(FlowElement):
    def process(self,elem={}):
        largs,kwargs=self.compute_args(elem)
        try:
            self.out_elem(getattr(self.connector,self.method)(*largs,**kwargs))
        except:
            error=traceback.format_exc()
            elem['error']=error
            self.error_elem(elem)



class ElementFilter(FlowElement):
    def __init__(self,filter=None):
        self.filter=filter
        self.out_objects=[NullProcessor()]
        self.error_objects=[NullProcessor()]
    def process(self,elem={}):
        if not self.filter or self.filter.evaluate(elem):
            self.out_elem(elem)

class ListAcumulator(FlowElement):
    def __init__(self):
        self.list=[]
        self.out_objects=[NullProcessor()]
        self.error_objects=[NullProcessor()]
    def process(self,elem={}):
        self.list.append(elem)
        self.out_elem(elem)

    def count(self):
        return len(self.list)

class BreakPoint(FlowElement):
    def __init__(self,*debug_vars):
        self.list=[]
        self.out_objects=[NullProcessor()]
        self.error_objects=[NullProcessor()]
        self.debug_vars=debug_vars
    def process(self,elem={}):
        import pdb
        pdb.set_trace()
        self.out_elem(elem)


class Printer(FlowElement):
    def __init__(self,prefix=''):
        self.prefix=prefix
        self.out_objects=[NullProcessor()]
        self.error_objects=[NullProcessor()]
    def process(self,elem):
        print self.prefix,elem
        self.out_elem(elem)

class ElementTransformer(FlowElement):
    def __init__(self):
        self.out_object=[NullProcessor()]
        self.error_objects=[NullProcessor()]
    def process(self,elem):
        self.out_elem(self.transform(elem))
    def transform(self,elem):
        return elem

class Ev(object):
    def __init__(self,expression):
        self.expression=expression

    def evaluate(self,elem):
        return eval(self.expression)

class TxIdWorkspaces(ElementTransformer):
    def transform(self,elem):
        print "elem",elem
        ids=[x['id'] for x in elem['workspaces']]
        elem['workspaces']=ids
        return elem

class TxIdWorkspace(ElementTransformer):
    def transform(self,elem):
        elem['workspace']=elem['workspace']['id']
        return elem

class TxProject(ElementTransformer):
    def transform(self,elem):
        elem['workspace']=elem['workspace']['id']
        elem['followers']=[x['id'] for x in elem['followers']]
        elem['members']=[x['id'] for x in elem['members']]
        return elem

class TxTask(ElementTransformer):
    def transform(self,elem):
        if elem['assignee']:
            elem['assignee']=elem['assignee']['id']
        elem['followers']=[x['id'] for x in elem['followers']]
        elem['hearts']=[x['id'] for x in elem['hearts']]
        if 9564532017776 in elem['hearts']:
            elem['hearts'].remove(9564532017776)
        elem['projects']=[x['id'] for x in elem['projects']]
        elem['tags']=[x['id'] for x in elem['tags']]
        elem['workspace']=elem['workspace']['id']
        if 'parent' in elem.keys() and elem['parent']:
            #elem['parent']=elem['parent']['id']
            del elem['parent']
        return elem


def test_list_generator():
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    coneptum_asana=ConeptumAsanaAPI('',debug=True)
    #ListProcessor(asana_api,'list_workspaces').out(Printer().process()
    #import pdb
    #pdb.set_trace()
    EvId=Ev("elem['id']")
    ListProcessor(asana_api,'list_workspaces').out(
        ElementProcessor(coneptum_asana,'_asana_put',(Ev("'workspaces/'+str(elem['id'])"),Ev("elem")))
    ).process()
    
    ListProcessor(asana_api,'list_workspaces').out(
        Printer('-Workspace:'),
        ElementFilter(Ev("elem['name']=='Coneptum'")).out(
            ListProcessor(asana_api,'list_users',[],{'workspace':EvId}).out(
                   Printer("--User"),
                   ElementProcessor(asana_api,'user_info',[EvId],{}).out(
                         Printer(),
                         TxIdWorkspaces().out(
                            Printer("---User transformed"),
                            ElementProcessor(coneptum_asana,'_asana_put',(Ev("'users/'+str(elem['id'])"),Ev("elem"))),
                            )
                    )
                )
        )
    ).process()

    ListProcessor(asana_api,'list_workspaces').out(
        Printer('-Workspace:'),
        ElementFilter(Ev("elem['name']=='Coneptum'")).out(
            ListProcessor(asana_api,'get_tags',[],{'workspace':EvId}).out(
                   Printer("--Tags"),
                   ElementProcessor(asana_api,'get_tag',[EvId],{}).out(  
                       Printer('----Tag detail'),
                       TxIdWorkspace().out(
                            Printer("Tag transformed"),
                            ElementProcessor(coneptum_asana,'_asana_put',(Ev("'tags/'+str(elem['id'])"),Ev("elem"))),
                            )
                   )                
                )
        )
    ).process()

    ListProcessor(asana_api,'list_workspaces').out(
        Printer('-Workspace:'),
        ElementFilter(Ev("elem['name']=='Coneptum'")).out(
            ListProcessor(asana_api,'list_projects',[],{'workspace':EvId,'include_archived':False}).out(
                   Printer("--Projects"),
                   ElementProcessor(asana_api,'get_project',[EvId],{}).out(  
                       Printer('----Project detail'),
                       TxProject().out(
                            Printer('-----Project transformed'),
                            ElementProcessor(coneptum_asana,'_asana_put',(Ev("'projects/'+str(elem['id'])"),Ev("elem"))),
                            )
                   )                
                )
        )
    ).process()


    ListProcessor(asana_api,'list_workspaces').out(
        Printer('-Workspace:'),
        ElementFilter(Ev("elem['name']=='Coneptum'")).out(
            ListProcessor(asana_api,'list_projects',[],{'workspace':EvId,'include_archived':False}).out(
                   Printer("--Projects"),
                   ListProcessor(asana_api,'get_project_tasks',[EvId],{}).out(
                        Printer("----Tasks"),
                        ElementProcessor(asana_api,'get_task',[EvId],{}).out(
                            Printer("----Task detail"),
                            TxTask().out(
                                Printer('-----Task transformed'),
                                ElementProcessor(coneptum_asana,'_asana_put',(Ev("'tasks/'+str(elem['id'])"),Ev("elem")))
                            ),
                        ),
                    )             
                )
        )
    ).process()


if __name__=='__main__':
    test_list_generator()

