
from package import app
import os


   
if __name__=='__main__':
    app.run(debug=True)
    print(os.environ.get("APIKEY"))
    print(os.environ.get("WORK"))
