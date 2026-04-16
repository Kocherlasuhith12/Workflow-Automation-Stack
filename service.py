import restate
from restate import Service, Context

# Define a Restate service called "greeter"
greeter = Service("greeter")


@greeter.handler()
async def greet(ctx: Context, name: str) -> str:
    """
    Restate handler: receives a name, returns a greeting.
    Called by Temporal activity at: POST /greeter/greet
    """
    greeting = f"Hello, {name}! Greetings from Restate 🎉"
    print(f"[Restate] greet called with name={name}")
    return greeting


# Start the Restate HTTP server on port 9080
app = restate.app(services=[greeter])

if __name__ == "__main__":
    import hypercorn.asyncio
    import asyncio
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:9080"]
    asyncio.run(hypercorn.asyncio.serve(app, config))