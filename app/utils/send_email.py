import boto3
import os
from botocore.exceptions import ClientError
from dotenv import find_dotenv, load_dotenv

from app.utils.config import settings


class SendEmail:
    load_dotenv(find_dotenv())

    SENDER = settings.SENDER

    CONFIGURATION_SET = settings.CONFIGURATION_SET

    AWS_REGION = settings.AWS_REGION

    SUBJECT = settings.SUBJECT

    CHARSET = "UTF-8"

    def send_email(self, email, reset_link):
        BODY_HTML = f"""<html>
        <head></head>
        <body>
        <h1>You have requested to reset your password</h1>
        <p>We cannot simply send you your old password. A unique link
        to reset your password has been generated for you. To reset your
        password, click the following link and follow the instructions.</p>
        <a href="{reset_link}">Reset Password</a>
        </body>
        </html>
                """

        client = boto3.client("ses", region_name=self.AWS_REGION)
        try:
            response = client.send_email(
                Destination={
                    "ToAddresses": [
                        email,
                    ],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": self.CHARSET,
                            "Data": BODY_HTML,
                        },
                    },
                    "Subject": {
                        "Charset": self.CHARSET,
                        "Data": self.SUBJECT,
                    },
                },
                Source=self.SENDER,
                ConfigurationSetName=self.CONFIGURATION_SET,
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! Message ID:"),
            print(response["MessageId"])


send_recover_email = SendEmail()
