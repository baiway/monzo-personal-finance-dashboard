# type: ignore # ignore Pylance warnings in this file as FastHTML is not
# compatible with Pylance.
# See: https://github.com/AnswerDotAI/fasthtml/issues/329#issue-2471897892
import requests
import uvicorn
from fasthtml.common import *
from datetime import datetime, timedelta
from src.utils import gen_rand_str, get_update_date, has_entries
from src.monzo_api import fetch_transactions
from src.dashboard_components import plot_spending_by_category

# URL Constants
BASE_AUTH_URL = "https://auth.monzo.com/"
TOKEN_URL = "https://api.monzo.com/oauth2/token"
REDIRECT_URI = "http://localhost:5001/auth/callback"

# In-memory storage for the OAuth state and auth code
oauth_state = None
auth_code = None

def run_app() -> None:
    uvicorn.run(
        create_app,
        host="localhost",
        port=5001,
        reload=False,
        factory=True
    )


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

    Returns:
        app: A FastHTML application instance ready to be served.
    """

    # If `data/transactions.db` does not already exist, create it
    db = database("data/transactions.db")
    transactions = db.t.transactions

    if transactions not in db.t:
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

    # Similarly, define a `Credentials` dataclass to pass to the `/auth`
    # handler. This gets automatically instantiated when the user enters
    # their `client_id` and `client_secret` on the `/auth` page
    @dataclass
    class Credentials:
        client_id: str
        client_secret: str

    # Similarly, define start and end dates for the date-picker
    @dataclass
    class Dates:
        start_date: str
        end_date: str

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
        timestamp = req.scope["auth_timestamp"] = sess.get("auth_timestamp", None)
        if timestamp is not None:
            expired = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") >= timedelta(minutes=5)
        if not auth or expired:
            return RedirectResponse("/auth", status_code=303)

    # Create a Beforeware object that blocks the user from manually accessing
    # all URLs except `/auth.*` until they've authenticated but still allows
    # stylesheets to be applied. `skip` is a list of regexes of routes that
    # are ignored here.
    bware = Beforeware(
        before,
        skip=[r".*\.css", "/auth.*"]
    )

    # Used in `exception_handlers` dict
    def _not_found(*args):
        return Titled("Oh no!", Div("We could not find that page :("))

    # Create FastHTML app
    app, rt = fast_app(
        before=bware,
        exception_handlers={404: _not_found},
        hdrs=(
            picolink,
            Style("""
                .indicator {
                    display: none;
                }
                .htmx-request .indicator {
                    display: inline-block;
                }
                button-content {
                    display: inline-block;
                }
                .htmx-request .button-content {
                    display: none;
                }
                .date-picker {
                    width: auto;
                }
            """)
        )
    )

    # Everything below this point is a route handler.
    #
    ###########################################################################
    #
    # TODO implement the dashboard...
    #
    # FIXME currently have to refresh the page to change the date again
    @rt("/")
    def get(sess):
        """Handler for the root directory where the dashboard is
        displayed. No dashboard is rendered until a `start_date` and
        `end_date` is selected via the date-picker.
        """
        if has_entries():
            last_updated = get_update_date()
            update_message = f"Transactions last updated at {last_updated}."
        else:
            update_message = "Transactions database is empty."

        return Titled(
            "Dashboard",
            Div(
                P("Welcome to your dashboard!"),
                P(update_message, id="update-date"),
                P("Would you like to update the transactions?"),
                Button(
                    Span("Update transactions", _class="button-content"),
                    Span("Loading...", aria_busy="true", _class="indicator"),
                    hx_post="/update-transactions",
                    hx_target="#update-date",
                    hx_swap="innerHTML"
                ),
                Form(
                    Input(id="start_date", type="date", _class="date-picker"),
                    Input(id="end_date", type="date", _class="date-picker"),
                    Button("Update plots"),
                    hx_post="/update-plots",
                    hx_target="#dashboard-components",
                    hx_swap="innerHTML"
                ),
                Div(id="dashboard-components") # initially empty
            )
        )

    @rt("/update-transactions")
    def post(sess):
        """Fetches transactions via Monzo's API and updates
        `data/transactions.db`. Returns the date and time of the update
        so that it can be displayed on the page.
        """
        access_token = sess["access_token"]
        fetch_transactions(access_token, verbose=True)
        last_updated = get_update_date()
        update_message = f"Transactions last updated at {last_updated}."
        return update_message

    @rt("/update-plots")
    def post(dates: Dates, sess):
        """Updates dashboard plots to show data defined between the
        `start_date` and `end_date` defined using the date picker.
        """
        start_date = datetime.strptime(dates.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(dates.end_date, "%Y-%m-%d")
        # Return a tuple of HTML elements (likely all `Img` objects)
        return (
            plot_spending_by_category(start_date, end_date)
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
            sess["auth"] = True   # stops redirects from `before` function
            sess["auth_timestamp"] = strptime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
            txt = (
                "Monzo authentication successful! Please now authenticate via "
                "the Monzo app on your mobile device. Press the 'Proceed to "
                "Dashboard' button when you have done so."
            )
            return Titled(
                "Monzo Authentication",
                Div(txt),
                Button(
                   "Proceed to Dashboard",
                   onclick="window.location.href='/'"
               )
            )
        else:
            return Titled(
                "Error",
                Div(f"Failed to get access token: {response.status_code}")
            )

    return app
