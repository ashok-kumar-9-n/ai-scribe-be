def extract_request_details(req):
    request_details = {
        "request_url": req.url,
        "method": req.method,
        "headers": dict(req.headers),
        "request_body": req.get_data(as_text=True),
        "query_params": req.args.to_dict(),
        "remote_address": req.remote_addr,
        "content_type": req.content_type,
    }

    return request_details