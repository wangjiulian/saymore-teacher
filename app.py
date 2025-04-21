from flask import Flask, redirect, url_for, request, flash, render_template
from config import Config
from extensions import db, login_manager, migrate
from models.teacher import Teacher
from models.subject import Subject
from flask_wtf.csrf import CSRFProtect, CSRFError
from datetime import datetime
from create_app import create_app

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
