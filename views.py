import flask
from flask import render_template, request

from github_pr import fetchprstatus


def pr_status(owner=None, repo=None, token=None):

    if owner is not None and repo is not None and token is not None:
        resp = fetchprstatus(owner, repo, token)
    else:
        resp = '{"status":"failure","message":"invalid parameters"}'

    resp = flask.Response(resp)
    resp.headers['Content-Type'] = 'application/json'
    return resp


def info():
    return render_template('info.html')
