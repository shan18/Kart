# Kart
An E-commerce website built using Django.


### Features

- Send email verification link to users when they sign up.
- If there is a server error (code = 500), then an email is sent to the administrator notifying him of the error and the cause of the error.
- A Library view which contains a list of and gives the ability to download all the digital items that the customer has bought.
- Display product history in account settings which shows the products that the user has recently viewed.
- A separate analytics view for admin/staff members which shows a graph of all the product sales over the past days/weeks/months.


### Tools Used
- **Python** - Django
- **Javascript** - jQuery, Ajax, jsrender, Chart.js
- **Bootstrap**


### Third Party Services

The following third party applications were used in this project:  
- **Amazon Web Services (AWS)**: Stores all static and media files.
- **Heroku**: Used to deploy the project in production environment.
- **stripe**: Deals with payment related stuff.
- **sendgrid**: Used to send transactional emails like email-id verification, order completion etc.
- **mailchimp**: Used to send marketing emails to customers.


## Instructions for setting up the project

1. Clone the repository  
`git clone `

2. Create a virtual environment and install the requirements  
`pip install -r requirements.txt`

3. Rename the file **credentials-sample.py** in *src/kart/* to **credentials.py** and replace the value of `SECRET_KEY` with the secret key of your own project. To generate a new secret key
	- Go to terminal and create a new django project `django-admin startproject <proj-name>`.
	- Now get the value of `SECRET_KEY` in *settings.py* and use that as the secret key for the **kart project**.
	- Now delete that new django project.

4. **Stripe setup**:
	- Create an account on [stripe](https://stripe.com/).
	- Go to the **API** section on the left.
	- Fetch the values of tokens **Publishable key** and **Secret key** and add them to `STRIPE_PUBLISH_KEY` and `STRIPE_SECRET_KEY` in **credentials.py** respectively.

5. **Mailchimp setup**:
	- Create an account on [mailchimp](https://mailchimp.com/). While signing up set the company name to the name of the project.
	- Go to the tab **Lists** and click on a list. Navigate to the **Settings** tab and click on **List name and campaign defaults**. Get the **List ID** on the right and add it to `MAILCHIMP_EMAIL_LIST_ID` in **credentials.py**
	- Get the mailchimp data center. For example: `us17` (It will we visible in the url). Add it to `MAILCHIMP_DATA_CENTER` in **credentials.py**
	- Go to account settings, get the **API Key** and add it to `MAILCHIMP_API_KEY` in **credentials.py**

6. **Sendgrid setup**:
	- Create an account on [sendgrid](https://sendgrid.com/).
	- Add your sendgrid username and password to `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in **credentials.py** respectively.
	- Change the email and name in `DEFAULT_FROM_EMAIL` and `MANAGERS` in all *settings files* with your name and email.

7. **Amazon Web Services (AWS) setup**:  
	Follow this guide to setup AWS in the project: [AWS Setup](notes/aws_setup.md). After settings up AWS, add all the required values to **credentials.py** (mentioned under the comment *aws keys*).

8. **Heroku setup**:  
	Follow this guide to setup Heroku in the project: [Heroku Setup](notes/heroku_setup.md).

9. Run the following commands  
`python manage.py makemigrations`  
`python manage.py migrate`  
`python manage.py collectstatic`

10. If the products are not visible then follow the **Database reloading with fixtures** section in this [guide](notes/notes.md).


#### Note:

Due to size issues, only one protected media file has been uploaded. Add the others by uploading them in the **Django Admin**, inside the **Products** section.
