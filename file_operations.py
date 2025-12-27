import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, session
from werkzeug.utils import secure_filename
from db import LoginCredentials, MyDatabaseClass, DatabaseConnectionPool
from S3_bucket_uploader import S3FileClass
UPLOAD_FOLDER = r'C:\Users\UCKAN\Desktop\test'
                   
class FileClass():
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    def __init__(self, app, upload_folder) -> None:
        self.app = app
        self.db_pool = DatabaseConnectionPool(minconn=1, maxconn=10)
        self.app.config['UPLOAD_FOLDER'] = upload_folder
        self.file_operations()  # Initialize file operations
        self.user_db = MyDatabaseClass(self.db_pool, name=None, password=None, email=None, comments=None)

    
    def get_user_email(self):
        user_email = session.get('user_email')
        return user_email
        
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def check_the_request_file_part(self):

        if 'file' not in request.files:
                    flash('No file', 'error')
                    return redirect(url_for('userpage'))
    
    def check_the_file_name(self):
                # Check if the file has no name
                if request.files['file'].filename == '':
                    flash('No selected file', 'error')
                    return redirect(url_for('userpage'))
        
    
    def file_operations(self):         
        @self.app.route('/upload_file', methods=['GET', 'POST'])
        def upload_file():
            if request.method == 'POST':
                self.check_the_request_file_part()
                self.check_the_file_name() 
                user_email = self.get_user_email()               
                file = request.files['file']
                
                if not user_email:
                        flash('User not logged in', 'error')
                        return redirect(url_for('login')) 
                
                if file and self.allowed_file(file.filename) and self.app.config['FLASK_ENV'] == 'development':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))
                    flash('File successfully uploaded', 'success')
                    # Generate the image URL
                    image_url = request.url_root + url_for('uploaded_file', filename=filename).lstrip('/')
                               
                    if not self.user_db.save_img_url_to_db(image_url):
                        flash('Failed to save image URL to the database', 'error')  
                        
                    username = session.get('username')     
                    # Pass the image URL to the template
                    return render_template('userpage.html', filename=filename, image_url=image_url, username = username)
                else:
                    s3 = S3FileClass(self.app, file)
                    filename = secure_filename(file.filename)
                    if s3.upload_file():
                        flash('File successfully uploaded', 'success')
                        image_url = s3.get_s3_url()
                        print(image_url)
                        if not self.user_db.save_img_url_to_db(image_url):
                            flash('Failed to save image URL to the database', 'error')
                        username = session.get('username')
                        
                    username = session.get('username') 
                    return render_template('userpage.html', filename=filename, image_url=image_url, username = username)           
                    
            flash('Invalid file type', 'error')
            return redirect(url_for('userpage'))
        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            return send_from_directory(self.app.config['UPLOAD_FOLDER'], filename)        
                       
            
        