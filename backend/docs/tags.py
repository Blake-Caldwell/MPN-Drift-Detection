
tags_metadata = [
    {
        "name": "health",
        "description": "Displays the current status of the webpage if it currently running. Required for github action docker build",
    },
    {
        "name": "upload",
        "description": "Upload files and process them based on the configuration provided. This endpoint allows users to upload multiple files, including a configuration file and data files, for a specific site. The processing of these files involves reading the configuration, processing the data, and running machine learning models.",
    },
    {
        "name": "job",
        "description": "Retrieve the details of a specific job by its ID. This endpoint allows enable the ability to query the status and details of a specific job using its unique ID. Also request specific fields from the job details by providing a comma-separated list of field names.",
    },
    {
        "name": "jobresults",
        "description": "Retrieve the results of a specific job by its ID. This endpoint allows for the fetching of results of a job once it has been completed. It merges actual data with predicted data for each activity in the job and returns the merged data.",
    },
]


descr = """

This is a web-based solution designed to assist Idoba, a technology-focused company serving the mining and resources sector. The application utilises Idoba's Mine Performance Navigator (MPN) model, 
a composite AI model that learnspatterns of a mine site's performance. This solution provides a platform for visualising the MPN model's output and identifying potential drift. 
The system is designed to backtest and display MPN model metrics automatically. It accepts a selection of CSV files along with a configuration file and uses these to generate predictions for the data. These predictions are then used to determine 
if the AI model is drifting from expected performance.Developed using NextJS for the front end and FastAPI for the back end, 
this web-based solution offers a user-friendly interface for interacting with the MPN model's outputs

"""


