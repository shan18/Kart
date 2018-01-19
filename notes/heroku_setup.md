# Instructions for going live with Heroku

All the shell commands given in this file should be executed from within the **src/** directory.  
If you are using this project, then you won't have to do most of the steps as they have already been implemented.

1. Create a free account on [Heroku](https://www.heroku.com).

2. Download Heroku cli from here: [https://devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

3. #### git setup:
	- Create another git repository inside the **src/** folder: `git init`  
	This is done because git for the project is set outside the **src/** directory and this won't work on heroku.
	- After initializing *git*, a separate **.gitignore** and **requirements.txt** file is required inside the **src/** directory. This new **.gitignore** will be same as its parent except that it won't contain the **kart/credentials.py** file and thus, it will remain visible only to the heroku git repository. It also contains the file **local.py** which removes the *local settings* from the production environment and **.py[cod]** for heroku. [This step has already been done and setup]

4. If the installation of the packages was done from the **requirements.txt** earlier, then skip this step.  
Install Heroku requirements: `pip install psycopg2 dj-database-url gunicorn`

5. Check the python version on the system: `python -V` (In my system it is Python 3.6.4) and save it as `python-3.6.4` in a file **runtime.txt** inside **src/**

6. Create a file **Procfile** inside **src/** and store the following in it:  
`web: gunicorn dj-project.wsgi`

7. Login to Heroku: (Then enter the credentials)  
`heroku login`

8. Create Heroku Project:  
`heroku create <project-name>`

9. Provision Database Add-on:  
`heroku addons:create heroku-postgresql:hobby-dev`

10. Update Django Production Settings to use the heroku database. See step 9 in the **guide** (Link given below).

11. Disable Collectstatic in order to use static files from *AWS* which we will setup later:  
`heroku config:set DISABLE_COLLECTSTATIC=1`

12. Push the changes to the heroku server: `git push heroku master`

13. Make migrations to heroku: `heroku run python manage.py migrate`

14. Enter heroku bash: `heroku run bash` and create a superuser:  
`python manage.py createsuperuser`

15. If you want to use a custom domain, then add that domain to `ALLOWED_HOSTS` in **production.py**

16. Follow the **guide** (Link given below) from step 10 till step 16.
	- Environment variables can be added either through terminal or in heroku: `Settings --> Config Variables`
	- Add the environment variable values without any quotes.
	- Also add all the api keys from stripe, mailchimp, aws etc. as environment variables.
	- We keep the old stripe keys in **kart/credentials.py** as default because for going live, stripe requires us to generate a live key which will go into the heroku environment variables.
	- After adding the environment variables in heroku server, replace the key values in project with `os.environ.get()`
	- For **AWS** (we will setup AWS after the project has been successfully setup with heroku), keep the default keys in credentials, this allows different developers to use their own keys for testing. This allows them to make tests on a small scale without using the actual data.
	- After updating the environment variables in herkou, restart the server from `More --> Restart all dynos`


### Note:

- **Guide** Link: [Go Live with Django & Heroku](https://www.codingforentrepreneurs.com/blog/go-live-with-django-project-and-heroku/)

- When changes are made to the models, run `makemigrations` locally first, then push the changes to heroku and then run `migrate` on the production server. (This is because, if any error occurs in models, then we can fix it locally first.)

- Whenever some changes are made to the environment variables in herkou, restart the server from `More --> Restart all dynos`


# Using Heroku locally

It maybe the case sometimes that the project needs some files from heroku to run locally. In that case, the project can be run locally using the **heroku cli**.

- #### Run the cli
    - To run the project, activate the virtual environment(if any) and run:  
    `heroku local`
    - By default, heroku uses **port 5000**, to use some other port (say 8000):  
    `heroku local -p 8000`

- This method uses the *local settings* file: **local.py** (whether or not it exists in *.gitignore*) and the local database **db.sqlite3**

- Whenever some changes are done, the heroku cli needs to be restarted manually (It does not refresh automatically).

- #### Fetching Environment Variables  
    To reveal all the configuration (environment) variables of the project in heroku server  
    `heroku config`  
    To get a specific value (say MAILCHIMP\_API\_KEY)  
    `heroku config:get MAILCHIMP_API_KEY`

- #### Using Environment variables in local project
    - Get all the environment variables into the local project and still keep them hidden, write them into a file called **.env** inside **src/** and update the **.gitignore**  
    `heroku config -s >> .env`
    - Then update **local.py** to use `os.environ.get()` for all environment variables.
    - With this, heroku cli will fetch the environment variables from the **.env** file.
    - This method will give an error with `python manage.py runserver`, so for that, add a default in `os.environ.get()` to get the environment variables from **kart/credentials.py**

- Using only heroku cli for running projects locally (without setting a default in `os.environ.get()`) and using the method above to get environment variables allow the sensitive information to stay hidden if we do not want to use the logic for storing keys in **kart/credentials.py** and plan on publishing the code to github.