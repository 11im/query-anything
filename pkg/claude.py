import anthropic

def request(db, schema, req, key):
    client = anthropic.Anthropic(api_key = key)
    msg = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
            {"db":db, "context":schema, "content":req}
        ]
    )
    return msg