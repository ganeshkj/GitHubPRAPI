import views


def urls():
    urls = [
        ('/', 'index', views.pr_status),
        ('/<owner>/<repo>/<token>/', 'pr_api', views.pr_status),
        ('/info', 'info', views.info),
    ]

    return urls
