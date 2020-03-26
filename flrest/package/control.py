from package import app
from .views import Edituser,Login,Collect,Category







app.add_url_rule('/user', view_func=Edituser.as_view('Euser'))
app.add_url_rule('/login',view_func=Login.as_view('login'))
app.add_url_rule('/collect',view_func=Collect.as_view('collect'))
app.add_url_rule('/category',view_func=Category.as_view('category'))