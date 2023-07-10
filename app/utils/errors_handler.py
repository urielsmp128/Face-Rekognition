responses = {
    200: ("OK", "Request fulfilled, document follows"),
    201: ("Created", "Document created, URL follows"),
    202: ("Accepted", "Request accepted, processing continues off-line"),
    203: ("Non-Authoritative Information", "Request fulfilled from cache"),
    204: ("No Content", "Request fulfilled, nothing follows"),
    400: ("Bad Request", "Bad request syntax or unsupported method"),
    401: ("Unauthorized", "No permission -- see authorization schemes"),
    403: ("Forbidden", "Request forbidden -- authorization will not help"),
    404: ("Not Found", "Nothing matches the given URI"),
    405: (
        "Method Not Allowed",
        "Specified method is invalid for this server.",
    ),
    409: ("Conflict", "Request conflict."),
    500: ("Internal Server Error", "Server got itself in trouble"),
}
