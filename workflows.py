from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import call_restate_activity


@workflow.defn
class MyWorkflow:

    @workflow.run
    async def run(self, name: str) -> str:
        """
        Temporal Workflow:
        1. Receives a name
        2. Calls Restate via an Activity
        3. Returns the final result
        """
        result = await workflow.execute_activity(
            call_restate_activity,
            name,
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        return f"Workflow completed for: {result}"