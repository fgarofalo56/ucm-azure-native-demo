"""Azure Functions app with Event Grid trigger for PDF conversion."""

import azure.functions as func

from pdf_converter import handle_blob_created

app = func.FunctionApp()


@app.function_name(name="pdf_converter")
@app.event_grid_trigger(arg_name="event")
async def pdf_converter(event: func.EventGridEvent) -> None:
    """Event Grid trigger: converts uploaded documents to PDF."""
    await handle_blob_created(event)
