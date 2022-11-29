# Kart

### Disclaimer: A Demo of this project was hosted on the free dynos on Heroku but now since Herko have stopped the support for free dynos, a demo of the project is no longer available.

An E-commerce website built using Django.  
URL: [https://shan-kart.herokuapp.com/](https://shan-kart.herokuapp.com/)

### Features

- Send email verification link to users when they sign up.
- Render order summary as invoice pdf and send them to users after the transaction has been completed.
- If there is a server error (code = 500), then an email is sent to the administrator notifying him of the error and the cause of the error.
- A Library view which contains a list of and gives the ability to download all the digital items that the customer has bought.
- Display product history in account settings which shows the products that the user has recently viewed.
- A separate analytics view for admin/staff members which shows a graph of all the product sales over the past days/weeks/months.

**Note**:  
To use the payment api of the website, use the following dummy cards:  
4242 4242 4242 4242&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Visa  
5555 5555 5555 4444&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mastercard  
Enter any 5-digit number for CVC and any future date for expiry.

### Tools Used

- **Python** - Django
- **Javascript** - jQuery, Ajax, jsrender, Chart.js
- **Bootstrap**

### Third Party Services Used

- **Amazon Web Services (AWS)**: Stores all static and media files.
- **Heroku**: Used to deploy the project in production environment.
- **stripe**: Deals with payment related stuff.
- **sendgrid**: Used to send transactional emails like email-id verification, order completion etc.
- **mailchimp**: Used to send marketing emails to customers.

## Instructions for setting up the project

1. Clone the repository  
   `git clone https://github.com/shan18/Kart.git`

2. Create a virtual environment and install the requirements  
   `pip install -r requirements.txt`  
   After installing the requirements, install this package separately  
   `pip install --pre xhtml2pdf`

3. Rename the file **credentials-sample.py** in _src/kart/_ to **credentials.py** and replace the value of `SECRET_KEY` with the secret key of your own project. To generate a new secret key

   - Go to terminal and create a new django project `django-admin startproject <proj-name>`.
   - Now get the value of `SECRET_KEY` in _settings.py_ and use that as the secret key for the **kart project**.
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

   - Create an account on [sendgrid](https://sendgrid.com/) and create an API key.
   - Add your sendgrid API key to `EMAIL_HOST_PASSWORD` in **credentials.py** respectively.
   - Change the email and name in `DEFAULT_FROM_EMAIL` and `MANAGERS` in all _settings files_ with your name and email.

7. **Amazon Web Services (AWS) setup**:  
   Follow this guide to setup AWS in the project: [AWS Setup](notes/aws_setup.md). After settings up AWS, add all the required values to **credentials.py** (mentioned under the comment _aws keys_).

8. **Heroku setup**:  
   Follow this guide to setup Heroku in the project: [Heroku Setup](notes/heroku_setup.md).

9. Run the following commands  
   `python manage.py makemigrations`  
   `python manage.py migrate`  
   `python manage.py collectstatic`

10. Now load the **products** and the **tags** into the database  
    `python manage.py loaddata products/fixtures/products.json`
    `python manage.py loaddata tags/fixtures/tags.json`

#### Note:

- The **Contact** page in the repository has been currently disabled, to enable it uncomment `line 17 in src/kart/urls.py` and `line 30-32 in src/templates/base/navbar.html`.
- The project contains _two level git architecture_, inner for heroku and outer for GitHub. Thus, the reason for _two .gitignore and requirements.txt files_.
- Due to size issues, only one protected media file has been uploaded in GitHub. Add the others by uploading them in the **Django Admin**, inside the **Products** section.
