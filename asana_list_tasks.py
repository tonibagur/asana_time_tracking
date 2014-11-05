from asana import asana

def get_all_users():
    asana_api = asana.AsanaAPI('2vzk6F5m.kow34uB7cmjXnebCK0NBbYI', debug=False)
    myspaces = asana_api.list_workspaces()
    coneptum_space = [s for s in myspaces if s['name']=='Coneptum'][0]
    print asana_api.list_users(coneptum_space['id'])


if __name__=='__main__':
    get_all_users()