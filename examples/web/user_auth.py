from flask import Flask, request
import replit

app = Flask(__name__)

@app.route('/')
@replit.web.authenticated(login_res=f"Hello! {replit.web.sign_in_snippet}")
def user_info():
    user = replit.get_user_info(request)
    if user:
        profile_image = user.profile_image
        username = user.name
        if profile_image and profile_image:
            return f"Username: {username}\n PFP: {profile_image}"

    return "User Info not available."

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
