# Instructions for using AWS S3 Static and Media Files

**Guide**: [S3 Static & Media Files for Django](https://www.codingforentrepreneurs.com/blog/s3-static-media-files-for-django/)  
If you are using this project, then you won't have to do most of the steps as they have already been implemented.


## AWS Setup

1. Follow step 1 and step 2 from the *guide*
    - While creating an **IAM User**, there will be an option to add the user to a group. Click on that and create a new group.
    - Go to the *Permissions* tab and click on *Attach Policy*.
    - Paste the policy given in *JSON* format in the **guide** in step 5 and save it (Replace `<your_bucket_name>` in the policy with the name of the bucket that you'll create in step 3).
    - Then attach the policy to the group. These policies give the users in the group permissions to access the services.

2. Follow step 3 from the **guide**
    - Select **Region** such that it has both versions 2 & 4 supported. In my case, the region is `ap-southeast-1`  
    For reference, see: [AWS Regions and Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region)
    - Keep other settings as the default ones and create the bucket.

3. Now go to the bucket created above and click on the *Permissions* tab. Go to *CORS Configuration* and click on *Save* (We will use the default configuration already written there).


## Django Setup

1. Follow step 1 till step 3 from the **guide** 
    - **boto** and **boto3** are python bindings for *AWS*. **django-storages** are used by django to send static files to *AWS*.
    - Add `storages` app to every settings module.
    - We migrate because we added a new app **storages**.

2. Add the required credentials of the IAM user and AWS to **kart/credentials.py** (See **kart/credentials-sample.py** for reference).

3. Follow the **guide** from step 4 till step 7
	- In step 4, create directory inside **kart/** folder and add a **__init__.py** file to make it a module, and then create **utils.py**
	- Create the static and media folder in the bucket (created above) as specified in **utils.py**. Make those folders public in *AWS*. Create another folder in the bucket called **protected/** (do not make it public), it can be used to store private static files.
	- In **kart/aws/conf.py**, update the `S3DIRECT_REGION`, app name (app name == **kart**) in `DEFAULT_FILE_STORAGE`, `STATICFILES_STORAGE` and bucket name in `AWS_STORAGE_BUCKET_NAME`.
	- set attribute `AWS_QUERYSTRING_AUTH = True` in **conf.py**
	- In step 7, do the import in *local settings*: **kart/settings/local.py** file.

4. Now, test it in local. Run `python manage.py collectstatic`. It will collect all the static files and now it should be visible in AWS bucket.

5. Now if we run the server in local, and inspect an image, the image source will give the AWS link.

6. On opening the image source link, our access key and other info will be visible in the url. To disable that, set `AWS_QUERYSTRING_AUTH = False` in **conf.py**

7. If we want to hide the static files, we can make the static folder in the AWS bucket to not public.

8. Now test it in production, add the *aws.conf* import in *production settings*: **kart/settings/production.py**. We can now remove the static and media root stuff from *production settings*, but we keep it just to be on the safe side.

9. After pushing the changes, migrate on the production server:  
`heroku run python manage.py migrate`


### Note

- Any existing media files (before the AWS setup) cannot be uploaded to the bucket automatically, they have to be manually uploaded either from AWS website, Django admin or through aws-cli. For cli, see: [AWS CLI Setup](https://aws.amazon.com/getting-started/tutorials/backup-to-s3-cli/)  
Once AWS has been setup, all media files will be directly uploaded to AWS bucket.
- Everytime any static or public-media file is added, the folder has to be made public again.
- For testing, to disable the AWS upload and use the local static files, comment out the *AWS conf.py* import from the *settings* of all environments.


## File Uploads

1. To link the view with the uploaded files in AWS, one way is to link the view with the file by using the path of the file in AWS. This method is very useful in case of large uploads because if the file changes then only the file path has to be updated in the database.  
The other way is to use a Django `FileField`, this method is not suitable for large file uploads.

2. If the same media file is uploaded to the same location, then by default AWS does not change its name and store it (like django does). AWS overwrites the previous file.