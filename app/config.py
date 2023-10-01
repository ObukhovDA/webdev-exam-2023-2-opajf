import os

SECRET_KEY = ''

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_2222_exam:@std-mysql.ist.mospolytech.ru/std_2222_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')

MIME_TYPES = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/png', 'image/svg+xml', 'image/tiff'
             'image/vnd.microsoft.icon', 'image/vnd.wap.wbmp', 'image/webp']
