from composio import ComposioToolSet, App
from composio.client.exceptions import NoItemsFound


app_to_connect = App.GOOGLECALENDAR  # can also be gmail, github, etc.

def get_user_id(username):
    toolset = ComposioToolSet(entity_id=username)
    entity = toolset.get_entity()
    return entity

def create_url(username):
    entity = get_user_id(username)  # Call get_user_id with the provided username
    try:
        entity.get_connection(app=app_to_connect)

        print(f"User {username} is already authenticated with {app_to_connect}")

    except NoItemsFound as e:
        # Create a request to initiate connection
        request = entity.initiate_connection(
            app_to_connect, redirect_url="https://google.com"
        )
        return request.redirectUrl
    
    

