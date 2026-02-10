from app import create_app

import traceback

app = create_app()

with app.app_context():
    client = app.test_client()
    # login as freelancer1
    try:
        resp = client.post('/login', data={'email':'freelancer1@example.com','password':'password123'}, follow_redirects=True)
        print('login status', resp.status_code)
    except Exception:
        print('login exception:')
        traceback.print_exc()

    # request browse-jobs
    try:
        r = client.get('/browse-jobs')
        print('/browse-jobs', r.status_code)
        # print small preview
        print(r.get_data(as_text=True)[:400])
    except Exception:
        print('/browse-jobs exception:')
        traceback.print_exc()

    # request my-bids
    try:
        r2 = client.get('/my-bids')
        print('/my-bids', r2.status_code)
        print(r2.get_data(as_text=True)[:400])
    except Exception:
        print('/my-bids exception:')
        traceback.print_exc()
