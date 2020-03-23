
from package import app
import os


   
if __name__=='__main__':
    print(os.environ.get("APIKEY"))
    print(os.environ.get("WORK"))
    app.run(debug=True)
