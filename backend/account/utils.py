from django.template.loader import render_to_string


def otp_mail(email,code,store_name):
    text_content = render_to_string(
        'emails/otp.html',
        context={
            'store_name': store_name,
            'user_name': email,
            'otp': code
        }
    )
    return text_content

def base_mail(store_name,subject,content ):
    text_content = render_to_string(
        "emails/base.html",
        context={
            'store_name': store_name,
            'subject': subject,
            'content': content
        }
    )
    return text_content

