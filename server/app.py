import flask
from flask import request
from flask_api import FlaskAPI
from flask_login import LoginManager, current_user, login_user, login_required

app = FlaskAPI("studypath")
app.secret_key = 'asdf'
login_manager = LoginManager()
login_manager.init_app(app)


from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))


def is_safe_url(target):
    from urllib.parse import urlparse, urljoin
    from flask import request, url_for
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

class User:

    def __init__(self, wuteva):
        self.uuid = '11'

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return str(self.uuid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User('TODO')
        login_user(user)
        next = request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)
        return {"message": "login successful"}
    return {
        "current_user": str(current_user)
    }


@login_manager.user_loader
def load_user(user_id):
    return User('TODO')


@app.route("/courses", methods=['GET', 'POST'])
@login_required
def courses():
    if request.method == 'POST':
        slug = request.data['slug']
        with driver.session() as s:
            results = s.run('''
            MERGE (:User {uuid: {uuid}})-[:OWNS]->(c:Course {slug: {slug}})
            RETURN c
            ''', {'uuid': current_user.uuid, 'slug': slug})
            # import pudb; pudb.set_trace()
            return {
                'results': [r['c']['slug'] for r in results]
            }
    else:
        with driver.session() as s:
            results = s.run('''
            MATCH (:User {uuid: {uuid}})-[:OWNS]->(c:Course)
            RETURN c
            ''', {'uuid': current_user.uuid})
            return {
                'results': [r['c']['slug'] for r in results]
            }


@app.route("/courses/<string:slug>/terms/<int:wpid>", methods=['GET', 'PUT', 'DELETE'])
@login_required
def course_assign(slug, wpid):
    with driver.session() as s:
        if request.method == 'PUT':
            s.run('''
                MATCH (:User {uuid: {uuid}})-[:OWNS]->(c:Course {slug: {slug}})
                MERGE (c)-[:CONTAINS]->(:Page {wpid: {wpid}})
            ''', {
                'uuid': current_user.uuid,
                'slug': slug,
                'wpid': wpid
            })
        elif request.method == 'DELETE':
            s.run('''
                MATCH (:User {uuid: {uuid}})-[:OWNS]->(c:Course {slug: {slug}})
                MATCH (c)-[r:CONTAINS]->(:Page {wpid: {wpid}})
                DELETE r
            ''', {
                'uuid': current_user.uuid,
                'slug': slug,
                'wpid': wpid
            })
        else:
            return {
                'message': 'use PUT or DELETE'
            }
    return {
        'message': 'success'
    }




@app.route("/search/<string:q>", methods=['GET'])
@login_required
def search(q):
    with driver.session() as s:
        results = s.run(
            "MATCH (p:Page) WHERE p.titleLower =~ {q} return p LIMIT 25",
            {'q': q.lower() + '.*'}
        )
    return {
        'results': [
            {
                'title': r['p']['titleOriginal'],
                'wpid': r['p']['wpid'],
            }
            for r in results
        ]
    }

if __name__ == "__main__":
    app.run(debug=True)