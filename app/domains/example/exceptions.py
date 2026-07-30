from app.core.exceptions import ConflictError, NotFoundError


class ExampleNotFoundError(NotFoundError):
    code = "example_not_found"

    def __init__(self, example_id: int) -> None:
        super().__init__(f"Example {example_id} does not exist.", {"example_id": example_id})


class ExampleNameConflictError(ConflictError):
    code = "example_name_conflict"

    def __init__(self, name: str) -> None:
        super().__init__(f"Example named '{name}' already exists.", {"name": name})
