from asana import asana
from coneptum_asana import ConeptumAsanaAPI
from pyfbp import *

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

