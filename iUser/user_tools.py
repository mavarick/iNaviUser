# encoding:utf8


def get_user_info(request):
    user = request.user
    data = dict(username=user.username)
    return data


