
from functools import wraps
import http
from flask import current_app, jsonify, request
from app.models import Users
import jwt
import app
from logger import CustomLogger

logger=CustomLogger()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print(request.headers)
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            logger.info(token)
        if not token:
            return jsonify({
                'message':'Authentication token is missing',
                'error':'Unauthorized'
            }),http.HTTPStatus.UNAUTHORIZED
        
        try:
            logger.info(current_app.config['JWT_SECRET_KEY'])
            data = jwt.decode(token,current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            logger.info(data['user_id'])
            current_user = Users.get(data['user_id'])
            logger.info(current_user)
            if current_user is None:
                return jsonify({
                    'message':'Invalid aithentication token',
                    'error':'Unauthorized'
                }),http.HTTPStatus.UNAUTHORIZED

        except Exception as e:
            logger.error(e)
            return jsonify({'message':'Something went wrong'}),http.HTTPStatus.BAD_REQUEST
        
        return f(current_user,*args,**kwargs)
    
    return decorated
    