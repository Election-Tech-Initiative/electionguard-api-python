import strawberry
from fastapi import FastAPI

from strawberry.asgi import GraphQL

from ..graphql.schema.queries import query

schema = strawberry.Schema(query= query)


graphql_app = GraphQL(schema)

app = FastAPI()

app.include_router(graphql_app, prefix="/graphql")
