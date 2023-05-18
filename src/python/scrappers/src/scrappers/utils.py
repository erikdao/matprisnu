from datetime import datetime

from prefect.runtime import flow_run


def generate_flow_run_name():
    """Generate a flow run name."""
    flow_name = flow_run.flow_name
    flow_name = flow_name.replace(" ", "_").lower()
    return f"{flow_name}-on-{datetime.utcnow():%Y%m%d-%H%M%S}"
