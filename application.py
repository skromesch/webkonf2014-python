from flask import Flask, request, Response
from boto.dynamodb2.table import Table
from boto.compat import json
import boto
import os
import uuid

#If no .boto config file. Ex.: service run on Amazon
if not boto.config.has_section('Credentials'):
	boto.config.add_section('Credentials')
	boto.config.set('Credentials', 'aws_access_key_id', str(os.environ.get('AWS_ACCESS_KEY_ID')))
	boto.config.set('Credentials', 'aws_secret_access_key', str(os.environ.get('AWS_SECRET_KEY')))


'''
~/.boto
[Credentials]
aws_access_key_id = YOURACCESSKEY
aws_secret_access_key = YOURSECRETKEY
'''

application = Flask(__name__)

#Set application.debug=true to enable tracebacks on Beanstalk log output. 
#Make sure to remove this line before deploying to production.
application.debug=True
 
'''
curl -X GET http://localhost:5000/
'''
@application.route('/')
def index():
	return Response(json.dumps({'message':"Contact Service"}),  mimetype='application/json')
	return jsonify()

'''
curl -X GET http://localhost:5000/contact
'''
@application.route('/contact', methods=['GET'])
def get_all():
	try:
		contacts_table = Table('Contacts')
		contacts = contacts_table.scan()
		res = []
		for contact in contacts:
			res.append({ 'id':contact['id'], 'name':contact['name'], 'email':contact['email'],'age':str(contact['age'])})

		return Response(json.dumps(res),  mimetype='application/json')
	except Exception as e:
			return Response(json.dumps({'message' : str(e)}),  mimetype='application/json')		

'''
curl -X GET http://localhost:5000/contact/<id>
'''
@application.route('/contact/<id>', methods=['GET'])
def get_by_id(id):
	try:
		contacts_table = Table('Contacts')
		contact = contacts_table.get_item(id=id)
		res = { 'id':contact['id'], 'name':contact['name'], 'email':contact['email'],'age':str(contact['age'])}
		return Response(json.dumps(res),  mimetype='application/json')
	except Exception as e:
			return Response(json.dumps({'message' : str(e)}),  mimetype='application/json')		

'''
curl -X POST --data "name=test&email=test@test.com&age=76" http://localhost:5000/contact
'''
@application.route('/contact', methods=['POST'])
def create():
	try:
		contacts_table = Table('Contacts')
		id = uuid.uuid1()
		name = str(request.form['name'])
		age = int(request.form['age'])
		email = str(request.form['email'])
		res = contacts_table.put_item(data={
			'id'   : str(id),
			'name' : name,
			'email': email,
			'age'  : age
			})
		if res == True:
			return Response(json.dumps({'message' : 'saved'}),  mimetype='application/json')		
		else:
			return Response(json.dumps({'message' : 'notsaved'}),  mimetype='application/json')				
	except Exception as e:
			return Response(json.dumps({'message' : str(e)}),  mimetype='application/json')		

'''
curl -X PUT --data "name=test&email=test@test.com&age=76" http://localhost:5000/contact/<id>
'''
@application.route('/contact/<id>', methods=['PUT'])
def update(id):
	try:
		contacts_table = Table('Contacts')
		contact = contacts_table.get_item(id=id)
		name = str(request.form['name'])
		age = int(request.form['age'])
		email = str(request.form['email'])
		contact['name'] = name
		contact['age'] = age
		contact['email'] = email
		res = contact.save()
		if res == True:
			return Response(json.dumps({'message' : 'saved'}),  mimetype='application/json')		
		else:
			return Response(json.dumps({'message' : 'notsaved'}),  mimetype='application/json')		
	except Exception as e:
			return Response(json.dumps({'message' : str(e)}),  mimetype='application/json')		

'''
curl -X DELETE http://localhost:5000/contact/<id>
'''
@application.route('/contact/<id>', methods=['DELETE'])
def delete(id):
	try:
		contacts_table = Table('Contacts')
		contact = contacts_table.get_item(id=id)
		res = contact.delete()
		return Response(json.dumps({'message' : 'deleted'}),  mimetype='application/json')		
	except Exception as e:
			return Response(json.dumps({'message' : str(e)}),  mimetype='application/json')		

@application.errorhandler(404)
def not_found(error):
    return Response(json.dumps({'error': 'Not found'}), status=404,  mimetype='application/json')

@application.errorhandler(500)
def not_found(error):
    return Response(json.dumps({'error': str(error)}), status=500,  mimetype='application/json')

 
if __name__ == '__main__':
    application.run(host='0.0.0.0')



