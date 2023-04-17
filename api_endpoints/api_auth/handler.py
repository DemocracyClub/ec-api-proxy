import os

import psycopg2
from psycopg2 import extras as pg_extras

conn = psycopg2.connect(
    host=os.environ.get("POSTGRES_HOST"),
    database=os.environ.get("POSTGRES_DATABASE_NAME"),
    user="postgres",
    password=os.environ.get("POSTGRES_PASSWORD"),
)
cur = conn.cursor(cursor_factory=pg_extras.RealDictCursor)


def lambda_handler(event, context):
    if "token" not in event["queryStringParameters"]:
        raise Exception("Unauthorized")
    api_key = event["queryStringParameters"].get("token", None)
    authentication = {"data": {"auth_token": api_key}}

    cur.execute(
        """
        SELECT id, name, key
        FROM users_apikey
        WHERE key = %s
        LIMIT 1
        """,
        (api_key,),
    )
    result = cur.fetchone()
    if not result:
        raise Exception("Unauthorized")

    authentication["data"].update(result)

    return {
        "principalId": authentication["data"]["id"],
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*",
                }
            ],
        },
        "context": authentication["data"],
    }
