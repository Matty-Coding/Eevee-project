import typer
from app.auth.services import add_user
import asyncio

app = typer.Typer()


@app.command()
def create_user_cmd(
    username: str = typer.Option(..., "--username"),
    password: str = typer.Option(
        ...,
        "--password",
        prompt=True, hide_input=True
    ),
) -> None:
    print("Creating user...")
    asyncio.run(add_user(username, password))
    print("User created!")


if __name__ == "__main__":
    app()
