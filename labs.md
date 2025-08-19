# IDUG NA 2025 - Db2 Machine Learning Workshop Instructions

## 1. Requesting an IBM id
Go to this page and register for an IBMid: [Create an IBMid](https://www.ibm.com/account/reg/us-en/signup?formid=urx-19776)

You'll you fill in a 2-page form and submit the form. It doesn't require any credit card to get an IBM id. 

Complete page 1 of the IBM id request form and click next. 
![alt text](.images/image-16.png)

After you clicking next on page 1, the registration process will send a 7 digit verification token to the email address you entered on page 1. Copy that token and enter this on the 2nd page of the registration form below and click `Submit`.

![alt text](.images/image-17.png)

Shortly after you'll receive an email such as the following with a confirmation that your IBM id has been created. 

![alt text](.images/image-18.png)

Remember your IBM id and password in a secure place. You'll need them for requesting and accessing a Db2 ML workshop VM. 

It will take a couple minutes to submit the form and get an IBM id. 

Once you have an IBM id and its password, go to the next step. 

## 2. Accessing Your Workshop VM
Go to workshop attendee's page by either clicking [this](https://techzone.ibm.com/my/workshops/student/67c5c4eaa104117773f24811) or typing on your browser https://ibm.biz/idug-au-vm


It will ask you to sign in using your IBM id and password. Enter your IBM credentails and log in. After you reach the Workshop Attendee's page, you will see the following form. In this form, enter the workshop access code that you received from your instructor and click `Submit password/access code` button. 


you'll be taken to the 

![alt text](.images/image-9.png)

Next, this process will assign a workshop VM to your IBM id and direct you to your VM environment page as follows:
![alt text](.images/image-10.png)


On the `Your environment` page, scroll down until you see a section called `VM Remote Console`. Click the blue console link. 

![alt text](.images/image-14.png)


Clicking the blue console link will launch the following login window to your workshop VM. From this window, click `Open in a new window` to open this in a full-size browser tab, which will be easier to work with. 

![alt text](.images/image-15.png)

From this expanded login window, log in as db2inst1 user with the password that your instructor has provided you. 

## 3. Downloading the Workshop Code

2. Download lab code from db2ml-labs repo:
```shell
git clone https://github.com/shaikhq/db2ai-labs
```

3. Type `ls` to see the git repo folder, `db2ai-labs`, that you just downloaded. 
```shell
ls
```

4. Go to `db2ai-labs` directory:
```shell
cd db2ai-labs
```

5. See the content of `db2ai-labs` directory:
```shell
ls
```

- `idax` directory has the content of the first lab where you'll use Db2's in-database advanced analytics (IDAX) stored 
procedures for developing a machine learning (ML) model.

- `udf-py` directory has the content of the second lab where you'll create and deploy a Python udf at Db2.

- `udf-c` directory has the content of the second lab where you'll implement a vector similarity search use case with Db2.
