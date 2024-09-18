# type: ignore # ignore Pylance warnings in this file as FastHTML is not
# compatible with Pylance.
# See: https://github.com/AnswerDotAI/fasthtml/issues/329#issue-2471897892
import requests
import uvicorn
from fasthtml.common import *
from src.utils import gen_rand_str

def run_app() -> None:
    uvicorn.run(create_app, host="localhost", port=5001, reload=False, factory=True)


def create_app() -> FastHTML:
    """Creates and configures a FastHTML application that authenticates
    with Monzo's API and provides a simple dashboard interface. This
    function sets up the following components:
      - A database connection to store and retrieve user credentials
        and transaction data.
      - "Beforeware" (`beforeware`) to ensure only authenticated users
        can access the dashboard.
      - Routes for:
        - `/auth`: Allows users to authenticate with Monzo via OAuth2,
          providing a form for entering `client_id` and `client_secret`
          (obtained from https://developers.monzo.com).
        - `/auth/callback`: Handles the Monzo OAuth2 callback,
          exchanging the auth code for an access token.
        - `/dashboard`: Displays a simple dashboard to authenticated
          users.
        - `/`: the main entry point, which acts as a simple test page.

    Returns:
        app: A FastHTML application instance ready to be served.
    """
    # URL Constants
    BASE_AUTH_URL = "https://auth.monzo.com/"
    TOKEN_URL = "https://api.monzo.com/oauth2/token"
    REDIRECT_URI = "http://localhost:5001/auth/callback"

    # In-memory storage for the OAuth state and auth code
    oauth_state = None
    auth_code = None

    # If `data/transactions.db` does not already exist, create it
    db = database("data/transactions.db")
    transactions = db.t.transactions
    users = db.t.users

    if transactions not in db.t:
        users.create(
            dict(
                client_id=str,
                client_secret=str
            ),
            pk="client_id"
        )
        transactions.create(
            dict(
                created=str,
                amount=int,
                description=str,
                merchant_name=str,
                category=str,
                tags=str,
                address=str,
                website=str
            ),
            pk="id"
        )

    # The `.dataclass()` method creates a dataclass that defines the type
    # of database entries
    Transaction = transactions.dataclass()
    User = users.dataclass()

    # Similarly, define a `Credentials` dataclass to pass to the `/auth`
    # handler. This gets automatically instantiated when the user enters
    # their `client_id` and `client_secret` on the `/auth` page
    @dataclass
    class Credentials:
        client_id: str
        client_secret: str

    # The `before` function is a *Beforeware* function. These are functions
    # that run *before* a route handler is called.
    def before(req, sess):
        """Sets the `auth` attribute in the request scope and gets it from
        the session. The session is a Starlette session, which is a dict-
        like object that is cryptographically signed so it cannot be
        tampered with.

        The `auth` key in the scope is automatically provided to any
        handler that requests it and cannot be injected by the user with
        query params, cookies, etc. so it should be secure to use.

        Taken from:
        https://github.com/AnswerDotAI/fasthtml/blob/main/examples/adv_app.py
        """
        auth = req.scope["auth"] = sess.get("auth", None)
        print(f"{auth = }")
        if not auth:
            return RedirectResponse("/auth", status_code=303)

    # Create a Beforeware object that blocks the user from manually accessing
    # all URLs except `/auth` until they've authenticated (but still allows
    # stylesheets to be applied)
    bware = Beforeware(
        before,
        skip=[r".*\.css", "/auth"] # list of regexes to skip
    )

    # Used in `exception_handlers` dict
    def _not_found(*args):
        return Titled("Oh no!", Div("We could not find that page :("))

    # Create FastHTML app
    app, rt = fast_app(
        before=bware,
        exception_handlers={404: _not_found},
        hdrs=(picolink)
    )

    # Everything below this point is a route handler.
    #
    ###########################################################################
    #
    # This is the handler for the main application.
    # TODO print the time that `transactions.db` was last updated and ask
    # the user whether they'd like to refresh. If so, redirect to `/auth`;
    # if not, redirect to `/dashboard`.
    @rt("/")
    def get():
        return Titled(
            "Welcome",
            Div(P("A simple test app."))
        )

    # This handler displays a form allowing the user to enter their `client_id`
    # and `client_secret`.
    # TODO add instructions explaining how to get `client_id` and
    # `client_secret` from https://developers.monzo.com/ (see `README.md`).
    @rt("/auth")
    def get():
        """Creates a form with two input fields and a submit button."""
        frm = Form(
            Input(id="client_id", placeholder="Client ID"),
            Input(id="client_secret", placeholder="Client secret"),
            Button("Authenticate"),
            action="/auth",
            method="post"
        )
        return Titled("Authenticate with Monzo", frm)

    # This handler is called when a POST request is made to the `/auth` path
    # (i.e. when the user submits their `client_id` and `client_secret`).
    # The argument `creds` is an instance of the `Credentials` dataclass,
    # which is auto-instantiated from the form data.
    # TODO is it possible to display `auth_url` in a 'mini-browser'?
    @rt("/auth")
    def post(creds: Credentials, sess):
        global oauth_state
        if not creds.client_id or not creds.client_secret:
            return RedirectResponse("/auth", status_code=303)

        # Save `client_id` and `client_secret` to Starlette session
        sess["client_id"] = creds.client_id
        sess["client_secret"] = creds.client_secret

        # Generate a unique state token to protect against CSRF
        oauth_state = gen_rand_str()

        # Create the Monzo authorisation URL
        auth_url = (
            f"{BASE_AUTH_URL}?client_id={creds.client_id}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&state={oauth_state}"
        )

        # FIXME
        # Redirect user to `auth_url`
        return RedirectResponse(auth_url, status_code=303)

    # This handler is called after the user receives the authentication email
    # from Monzo. When the user clicks the "Log in to Monzo" button, they'll be
    # directed to http://localhost:5001/auth/callback?code=...
    # This handler extracts the authentication code from this URL, then
    # exchanges it with Monzo's servers to get an access token, which is needed
    # to make API requests.
    #
    # TODO can we make the URL tidier here? It's a mess and looks extremely
    # amateur
    #
    # TODO from a UX perspective, it would be very nice to include a screen
    # recording of a mobile device receiving the push notification from Monzo,
    # then tapping on it to authenticate via the app. It would make it a lot
    # easier for the user to understand what to do here.
    #
    # TODO before proceeding to the dashboard, include a check for whether
    # the user has authenticated via their mobile device as well (check for
    # an error code, then redirect back here)
    @rt("/auth/callback")
    def get(req, sess):
        global auth_code
        auth_code = req.query_params.get("code")
        state = req.query_params.get("state")
        client_id = sess["client_id"]
        client_secret = sess["client_secret"]

        # Verify the state token
        if state != oauth_state:
            return Titled(
                "Error",
                Div("Invalid state token. Authentication failed.")
            )

        # Exchange the authorization code for an access token
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": REDIRECT_URI,
                "code": auth_code,
            }
        )

        if response.ok:
            sess["access_token"] = response.json()["access_token"]
            txt = (
                "Monzo authentication successful! Please now authenticate via "
                "the Monzo app on your mobile device. Press 'Proceed' when "
                "you have done so."
            )
            return Titled(
                "Monzo Authentication",
                Div(txt),
                Button(
                   "Proceed to Dashboard",
                   hx_get="/dashboard",
                   hx_target="body"
               )
            )
        else:
            return Titled(
                "Error",
                Div(f"Failed to get access token: {response.status_code}")
            )


    # This handler displays the dashboard (not yet implemented)
    # FIXME
    @rt("/dashboard")
    def get():
        return Titled("Dashboard", Div("Welcome to your dashboard!"))

    return app
