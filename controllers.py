import models
import utils
import json


def register(handler, body):
    '''
    Create a new user in the database,
    handling validation and hashing of the password.
    '''
    # Parse request body
    json_body = json.loads(body)

    try:
        email = json_body['email']
        password = json_body['password']
    except KeyError:
        handler.response(400, 'Missing email or password')

    if not utils.valid_email(email):
        handler.response(400, 'Invalid email')
        return

    if not utils.valid_password(password):
        handler.response(400, 'Invalid password')
        return

    salt, hashed_password = utils.hash_password(password)
    verification_token = utils.get_email_verification_token(email)

    # Save user to database
    newUser = models.User(email, salt, hashed_password, verification_token)
    models.create_user(newUser)

    # Here we would send an email to the user with a link containing the token

    handler.response(200, "User created")


def verify_email(handler, body):
    '''
    If the supplied email and token match those stored in
    the database, mark the user as verified by removing the token
    '''
    # Parse request body
    json_body = json.loads(body)

    try:
        email = json_body['email']
        token = json_body['token']
    except KeyError:
        handler.response(400, 'Missing email or token')

    user = models.get_user_by_email(email)

    if user is None or user.email_verification_token != token:
        handler.response(401, 'Unauthorized')
        return

    # Remove the token from the database
    models.remove_email_verification_token(email)

    handler.response(200, "User updated")


def login(handler, body):
    '''
    If the supplied email and password match that in the database,
    authorize the login
    '''
    # Parse request body
    json_body = json.loads(body)

    try:
        email = json_body['email']
        password = json_body['password']
    except KeyError:
        handler.response(400, 'Missing email or password')

    user = models.get_user_by_email(email)

    valid_login = user and user.email_verification_token == None and utils.validate_password(
        password, user.salt, user.hashed_password)

    if valid_login:
        handler.response(200, "Authorized")
    else:
        handler.response(401, "Unauthorized")
