from util.authentication import find_auth
from util.database import get_sessions, get_sessions_for_branches, list_branch_codes
from flask import make_response, jsonify, request


def normalize_branches(branch_field):
    if branch_field is None:
        return []
    if isinstance(branch_field, list):
        branches = branch_field
    elif isinstance(branch_field, str):
        branches = [branch_field]
    else:
        branches = list(branch_field)
    return [str(item).strip() for item in branches if str(item).strip()]


def resolve_allowed_branches(admin):
    branches = normalize_branches(admin.get("branch") if admin else None)
    if not branches:
        return []
    if branches[0].lower() == "master":
        return list_branch_codes()
    return [b.upper() for b in branches]


def getSessions():
    auth_token = request.cookies.get("auth_token")
    admin = find_auth(auth_token) if auth_token else None
    allowed_branches = resolve_allowed_branches(admin)
    if not allowed_branches:
        res = make_response(jsonify({"error": "Branch not available"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code=403
        return res
    branch = request.cookies.get("branch")
    if branch and branch != "All":
        if branch not in allowed_branches:
            res = make_response(jsonify({"error": "Forbidden branch"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code=403
            return res
        sessions = get_sessions(branch)
    else:
        sessions = get_sessions_for_branches(allowed_branches)
    res = make_response(jsonify(sessions))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    return res


def getBranch():
    admin = getMe(True)
    allowed = resolve_allowed_branches(admin)
    branches = allowed
    if branches and len(branches) > 1:
        branches = ["All"] + branches
    res = make_response(jsonify({"branch":branches})) 
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    return res


def getMe(f: bool):
    auth_token = request.cookies.get('auth_token')
    admin = find_auth(auth_token)
    if admin:
        admin.pop("password", None)
        admin.pop("auth_token", None)
    #ret = {'username':admin.get('username'), 'employeeId':admin.get('id'),'firstName':admin.get('firstName'),'lastName':admin.get('lastName'), 'email':admin.get('email')}
    res = make_response(jsonify(admin))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    if f == False:
        return res
    else:
        return admin
