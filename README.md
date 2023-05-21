# flashcards-server
server for running Auto Flashcards Chrome Extension: https://github.com/JJJUhlar//auto-flashcards-plugin

## Setup

1. Fork / Clone the repo
2. Get / create openai api key: platform.openai.com
3. Create config files depending on whether you want to deploy locally or via heroku. 

### Deploy local development server

1. Make a `.env` file and a `.flaskenv` file. 
2. Add the following lines to your flask env:
`FLASK_APP=app`
`FLASK_ENV=development`
`FLASK_RUN_PORT=8080`
Feel free to use another port, but the chrome extension's default configuration will look for port 8080.
3. In your `.env` file first add your openai api key: `OPENAI_API_KEY=<PUT YOUR API KEY HERE>`
4. Also add the local configs for a Postgres DB of your choosing in the following format: 
`DATABASE=<PUT YOUR DATABASE HERE>`
`DBUSER=<PUT YOUR DATABASE USER HERE>`
`DPASS=<PUT YOUR DATABASE PASSWORD HERE>`
`DBHOST=<PUT YOUR DATABASE HOST HERE>`
5. Activate the virtual environment by opening the terminal in the repo and running `$ source venv/bin/activate` or `source venv\Scripts\activate` on Windows.
6. Initialise the database with some example flashcards by running python3 init_db.py
7. You can now run the local dev server by running `flask --app app run --debug`
8. Well done! You are now ready to try out Auto Flashcards once you've installed https://github.com/JJJUhlar//auto-flashcards-plugin

### Deploy via heroku
1. Login to Heroku and create a new app in your dashboard. Call it whatever you like, for example "Joe's flashcards"
2. Go to the settings panel for "Joe's Flashcards" where you can edit the configuration variables under the 'Config Vars' panel.
3. Add Keys for `OPENAI_API_KEY`, `DATABASE`, `DBUSER`, `DBPASS`, `DBHOST` and add the appropriate values, as described above.
4. Open the repo in your terminal and run `heroku login` and login
5. Push the repo to heroku by running `git push heroku main` 
6. Once the build is complete, all you need to do is update Auto Flashcards to connect to your new server
