# Signals

1. Default django signals are used to send a signal whenever an object is created or updated. To send a signal while viewing a page or viewing an object we need to define our own custom signals.

2. In order to implement such custom signals, we have to call those signals everytime the object view function is called or in every view function of the page. This method can be redundant because we have to write the same line in multiple places.

3. If we are using function-based views, then there is no option to overcome this redundancy.

4. For class-based views, this redundancy can be removed by creating **mixins**. With this, if something changes in the signal, we would only have to update the signal and the mixin.

5. After creating the mixin, import it in **views.py** and include the mixin as a parent class in the required class-based view.


# Models

1. #### Custom Model Managers:
	- These allow us to create our own object calling methods. Suppose we want to get the list of featured products, then we would have to use the method  
    `Product.objects.filter(featured=True)`
	- We can use custom managers to make these functions simpler. For this, create a new subclass of **models.Manager** and define the new function within it.  
    `Product.objects.featured()`
    - If any default query is overriden then the changes done to it will reflect even if a *reverse lookup* is performed.

2. #### Custom QuerySets:
We can't use the following command:  
`Product.objects.all().featured()`
For this, create a subclass of **models.query.QuerySet** in **models.py** and create the function within it. Then redefine the `get_queryset()` method in the Model manager.

3. `Product.objects.get(...)` function is always meant to return only one object. If more than 1 object exists it gives a **MultipleObjectsReturned error**. To get multiple objects, use `Product.objects.filter(...)` method.

4. #### Keys:
	- **ForeignKey**: It is a *Many to One* relationship. If model **A** has a foreign key of **B**. Then **A** can access **B** by **A.B** and **B** can reversely access **A** by **B.A_set.all()**.
	- **OneToOneField**: In this, the two objects must share a unique relationship. It is similar to `ForeignKey(model, unique=True)` with one exception that *OneToOneField* returns exactly one object while *ForeignKey* returns a queryset.
	- **ManyToManyField**: In this; zero, one or more objects of the first model may be related to zero, one or more objects of the second model. For example in the project, the models `Cart` and `Product` have this relationship. A cart can have multiple products and a product can belong to multiple carts.

5. By adding the decorator `@property` to a function inside the model class, the function can be simply accessed by *instance.function* [without paranthesis]

6. To use *OR operation* inside the querysets, a **lookup** module is required which can be fetched by `django.db.models.Q`. Example:  
`Model.objects.filter(Q(A=B) | Q(A=C))`


# Views

1. #### Decorators  
	- Decorators in django can be used to restrict access to views based on the request method. These decorators will return a **django.http.HttpResponseNotAllowed** if the conditions are not met.
	For class based views, decorators can be added in three ways:
    	- Overriding the `dipatch()` method and adding a decorator by  
	`@method_decorator(<decorator_name>)`
    	- Creating a mixin and overrding the `dispatch()` for that.
    	-  Use django's in-built mixins.
	- These decorators have their own default redirect url if the conditions are not met. To change those default redirect urls, we can set a `RedirectView` in **urls.py**, but this way is not robust. So a proper way of doing it is to override the django's defaults. The defaults can be overriden in *settings*, for example we can change the default for the `LoginRequiredMixin` by specifying a `LOGIN_URL`.

2. If the `redirect()` method is used by passing it a *view name*, the URL will be **reverse resolved** using the `reverse()` method.

3. To render out a string containing *html* having a *link* within it, it needs to *marked safe* first. This can be done by the in-built module `django.utils.safestring.mark_safe`. This ensures django that the link can be trusted and it is not submitted by the user.


# Some Built In Django Functionalities

1. #### Sending Email
    - The `django.core.mail.send_mail` module in django requires the content of the email to be an html page and those html pages should reside within the main **templates/** directory. This template can be fetched from the `django.template.loader.get_template` module.
    - The email can be send to multiple users by adding the email-ids in the `recipient_list`. This is sent as a **carbon copy**, so other recipients can see to whom this email was sent.

2. **Django's Built In Password Management** redirects the user to the django admin page for password changes. So it needs to be overridden.

3. For timezone related stuff, use `django.utils.timezone` instead of python's in-built `datetime` module because the `datetime` module does not consider the timezone specified in **settings.py**


# Miscellaneous

1. **FileWrapper**
To make a file downloadable through django, it's path has to be provided to the view. This method cannot work with protected files because their path is different from the default media root. Thus, to implement downloading of protected media files, a `FileWrapper` is used. After using a `FileWrapper`, only the **file_name** has to be provided for the downloaded file and with this the protected files are downloaded as well as their path remains hidden.


# Database reloading with fixtures

- With fixtures we can save desired database information before deleting the database, and then reload them back when a new database is created.

- This command displays all the database data in json format:  
`python manage.py dumpdata --format json --indent 4`

- This command displays data of a particular model in json format:  
`python manage.py dumpdata products.Product --format json --indent 4`

- This command stores data of a particular app in json format in a file:  
`python manage.py dumpdata products --format json --indent 4 > products/fixtures/products.json`

- After changing the database, load the data with the command:  
`python manage.py loaddata products/fixtures/products.json`

- To delete information of a particular app from database:
	- Remove the migrations folder of that app.
	- Save the existing data using fixtures of other apps
	- Delete the old database file and create a new one.
	- Run migrations.
	- Now load previous data using the loaddata command.


# Javascript

1. We keep the endpoints for the forms at action attribute because in case the user disables javascript for this website, then still the website will function normally as it used to do earlier without javascript.

2. So to use an API-endpoint for the javascript, we use the attribute **data-endpoint** in form and use that in our ajax code because if in future if we want to change the API or use RESTful APIs, then we would make changes only to **'data-endpoint'** in order to maintain the functionality mentioned in above. **data-endpoint** is just a made-up attribute, thus any changes to it never affect the functionality of the form.

3. By adding the **csrf ajax js**, we automate the csrf protection of the forms handled by any javascript or services like amazon s3 etc.

4. Adding attributes of a form inside the class of a container makes that container a form module. These form modules are created to make the forms reusable. One way of making them reusable is by using jsrender.

5. To make a form reusable:
	- Make a form module
	- Include the *form-html* inside the jsrender template. And keep the template inside the **verbatim** block.
	- Replace all django variables like `{{ name }}` inside the form html with jsrender variables `{{:name}}` (no spaces).
	- Keep the jsrender template inside the base js file, so that it can be accessed from anywhere.
	- Handle the form data by calling the template and rendering it with all the variables specified by the module.


# Static/Media/Templates

1. When uploading a file, add the media root to url patterns otherwise, the file will not be rendered during the display. For example: In image tag, it adds an incomplete style attribute.

2. In templates which are extending other template, codes written outside the blocks are not considered. Thus, if we want to take out some code, we can write it outside the blocks.

3. Inside a template, any code inside the block `{% verbatim %}{% endverbatim %}` is rendered as a plain template, so django variables `{{ name }}` won't be rendered.

4. `request.build_absolute_uri` gives the absolute url of the current page.

5. Custom error templates should be inside the root template directory (or root of an app template directory) with the following naming convention: `<error-code>.html`

6. The main **templates/** directory (as specified in **settings.py**) can override all the existing templates in the project.
	- To override any in-built template of a django module, see the directory in which the django module stores its templates (refer documentation) and create a custom template with same name and inside the same directory.
	- To override the templates of an app, create the new template inside the main **templates/** directory with the path `<app-name>/templates/<template-name>.html`

7. To add some **protected media** to the website, the upload path of that media should be different than the **media root**. This can be done by the `django.core.files.storage.FileSystemStorage`, this overrides the default storage location for any given field. And to make the uploaded media protected, store the location of the protected media inside the attribute `PROTECTED_ROOT` in **settings.py**

8. Slicing in for loops:  
Example - `{% for x in list|slice:"3:5" %}`


# URLs

1. By giving names to URLs, removes the concept of changing the url everywhere if a base url changes. URL shortcuts can be used in two ways: using `{% url 'name' <parameter if any> %}` in the template or by using reverse.

2. There can be a case where multiple apps have URLs with same names, in such cases, we need to use a namespace parameter in `include()` to differentiate between them.

3. While handling urls, for example in a form let the url be *localhost:8000/form*. Then the absolute endpoint based on the provided endpoint will be (notice the preceding slash):
	- data/ --> localhost:8000/form/data
	- /data/ --> localhost:8000/data


# Django files for Production Environment

1. #### Settings Module:
	- The **settings.py** file should be separate for debug and production environment or should be different if there are multiple django developers in the same project.
	- To use multiple settings file, create a directory named *'settings'* in the main app directory and create a file called **\_\_init__.py** inside it. This makes the *settings* directory as a package folder. Django will only check this file whenever *settings* is called.
	- To make django check the other settings file, do `from <file> import *` inside the **\_\_init__.py** to use the other settings modules.
	- Now, since the previous *settings.py* file was moved into the *settings/* folder, the `BASE_DIR` attribute in it now corresponds to the main app directory whereas the `BASE_DIR` attribute should point to the folder containing **manage.py**. So, add an extra `os.path.dirname()` to the `BASE_DIR` attribute.
	- In the **\_\_init__.py**, the import statement at the end of the file will override all the others. So, when working in an environment, make sure that the import for *settings* file for that environment is at the end of the file.
	- When working with production environment, we set the *local settings* file import in **\_\_init__.py** inside a `try` block to ignore the errors. Only when working with local, we take that import out of the `try` block. We never, put the *production settings* inside the `try` block because there shouldn't be any errors in the production environment.
	- Add **SSL/TLS** certificates to **production.py** for using **https** security for the website. See: [SSL/TLS Settings for Django](https://www.codingforentrepreneurs.com/blog/ssltls-settings-for-django/)

2. #### Database Folders
	- Generally, the database files are inside the *src/* directory. We can change that by adding a folder name to the path for database file in *settings.py* and then include a *__init__.py* file in that folder.
	- Creating a database folder helps when there are multiple django developers working on a project and each one first tests the changes on his own database before affecting the production database.

3. Choose a different `SECRET_KEY` for the production environment and keep that key secret. To get a new key:
    - Create a new django project `django-admin startproject <project-name>`
    - Get `SECRET_KEY` from its *settings* and use it for production.
    - Delete the new project.


# External APIs

1. If the API dows not have a *pip* package then we can handle the calls to that api urls by building a wrapper class in our project. This can be done by writing the class in **utils.py** file.

2. If we want to use a webhook for an api, then that api might need a callback url. Since, we do testing in **localhost**, we can use a service called **requestbin**. It provides us with demo urls which can capture the webhook data with which we can see the response and write code to handle it accordingly in our project. Then, when the project is live in an url, we can test our code by setting the appropriate webhook url.

3. We can't test the code for the webhook data in localhost because the data is sent to the url in a *post* method, and we can only access that url using *get* method.

4. While using webhooks, if we use class based views to handle post data then django requires *csrf*. So we add a **mixin class with csrf_exempt decorator** and make the webhook view *inherit* the mixin.


# Django Shell

- while filtering:
    - `Product.objects.filter(title__contains='shirt')`
    - `Product.objects.filter(title__icontains='shirt')` [case-insensitive]
    - `Product.objects.filter(title__contains='shirt', description__iexact='this')`
    - `Product.objects.get(pk=2)`  [id object does not exist, get gives an exception, while filter returns an empty result]

- Using `django.template.loader.get_template`:
	- Obtain the template: `temp = get_template('path')`  
	This can also fetch a *.txt* file.
    - Render the template: `temp.render(<context-if-any>)`  
        - This will give a warning when executing in shell because we are using `render()` outside the context processors.
        - If no context if given and the template contains context, it will not render out those variables.