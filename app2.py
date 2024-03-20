# from datetime import datetime
# import json
# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
# import mysql.connector
#
#
# app = Flask(__name__)
#
# # Load database configuration from JSON file
# with open('templates/config.json', 'r') as c:
#     db_config = json.load(c)["params"]
#
# # Configure SQLAlchemy with mysql-connector-python
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://root:root@localhost/food"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
#
# # Define Contact model
# class Contact(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(255), nullable=False)
#     message = db.Column(db.String(255), nullable=False)
#     date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#
# # Create tables
# db.create_all()
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
# @app.route('/contact', methods=['POST'])
# def contact():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         message = request.form['message']
#
#         try:
#             new_contact = Contact(name=name, email=email, message=message)
#             db.session.add(new_contact)
#             db.session.commit()
#             return 'Form submitted successfully!'
#         except Exception as e:
#             return 'Error submitting form: {}'.format(str(e))
#     return "Method not allowed"
#
# if __name__ == '__main__':
#     app.run(debug=True)
