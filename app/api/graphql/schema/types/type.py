import strawberry

@strawberry.type
class User:
    name: str
    age: int
