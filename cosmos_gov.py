from flask import Flask, render_template
import requests
import tomlkit
import logging
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Configure logging with UTF-8 encoding
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format, encoding="utf-8")

# Create a logger
logger = logging.getLogger("ProposalSummary")
logger.addHandler(logging.FileHandler("templates/proposal_summary.log", encoding="utf-8"))  # Save logs to a file with UTF-8 encoding

# Read configuration from TOML file
with open("config.toml", "r") as f:
    config = tomlkit.parse(f.read())

# Initialize an empty list to store the proposals
proposals = []


def check_api_path(base_api, paths):
    """
    Checks which API path is implemented and returns the first working path.
    If none of the paths work, returns None.
    """
    for path in paths:
        url = f"{base_api}{path}?pagination.limit=1000"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if not (data.get('code') == 12 and data.get('message') == "Not Implemented"):
                    return path  # This path works, return it
        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking API path {url}: {e}")
    return None  # No working path found


# Function to process proposals for a given chain
def process_chain(chain):
    # Define potential API endpoint paths
    paths = ["/cosmos/gov/v1/proposals", "/cosmos/gov/v1beta1/proposals"]
    api_eval_test = check_api_path(chain['api'], paths)
    chain_name = chain["displayname"]
    chain_id = chain["chain-id"]
    api_url = chain.get("api")
    api_gov_prop = chain.get("api_gov_prop", api_eval_test)

    logger.info(f"Identified API URL for chain: {api_eval_test}")

    try:
        logger.info(f"Querying API for chain: {chain_name}")

        if api_url is None:
            logger.warning(f"No API URL found for chain: {chain_name}")
            return []

        # Make the API request to fetch the proposals
        response = requests.get(f"{api_url}{api_gov_prop}?pagination.limit={limit}")
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()

        if data is None:
            logger.warning(f"Empty response received for chain '{chain_name}'")
            return []

        logger.info(f"Processing proposals for chain: {chain_name}")

        # Extract relevant information from the API response
        chain_proposals = []

        # Check if the proposals are nested within another key
        proposals_data = data.get("proposals", data.get("data", []))

        logger.info(f"Chain ID: {chain_id}, Number of proposals before processing: {len(proposals_data)}")

        for proposal in proposals_data:
            try:
                proposal_id = proposal.get("proposal_id", proposal.get("id", "N/A"))
                proposal_status = proposal.get("status", "N/A")
                proposal_content = proposal.get("content", proposal)
                # messages = proposal.get("messages", [])

                # proposal_type = proposal_content.get("@type", "N/A")
                proposal_type = proposal_content.get("@type") or next((message["@type"] for message in proposal_content.get("messages", []) if "@type" in message), "N/A")
                proposal_title = proposal_content.get("title", "N/A")
                voting_start_time = proposal.get("voting_start_time", "N/A")
                voting_end_time = proposal.get("voting_end_time", "N/A")

                logger.info(f"Processing proposal: {proposal_id}, Status: {proposal_status}")

                chain_proposals.append(
                    [chain_name, chain_id, proposal_id, proposal_type, proposal_title, proposal_status,
                     voting_start_time, voting_end_time]
                )

            except AttributeError as ae:
                logger.error(f"AttributeError occurred: {ae}, {chain_id}, {proposal_id}")
                continue  # Skip this proposal and continue with the next one

        logger.info(f"Chain ID: {chain_id}, Number of proposals after processing: {len(chain_proposals)}")

        return chain_proposals

    except requests.RequestException as e:
        logger.error(f"An error occurred while querying the API for chain '{chain_name}': {str(e)}")
        return [
            [
                chain_name,
                chain["chain-id"],
                0,
                "ERR",
                "ERR",
                "ERR",
                0,
                0
            ]
        ]

# Set the number of threads for concurrent execution
num_threads = 8  # Set the desired number of threads

# Set the number of proposals to be returned
limit = 2000  # Set the desired limit here

@app.route("/")
def index():
    # Render the loading template with the loading message
    return render_template("loading.html")

@app.route("/proposals")
def show_proposals():
    global proposals

    # Clear the proposals list before retrieving new data
    proposals.clear()

    # Create a thread pool executor
    executor = ThreadPoolExecutor(max_workers=num_threads)

    # Submit the tasks to the thread pool
    tasks = [executor.submit(process_chain, chain) for chain in config["chains"]]

    # Retrieve the results from the tasks
    for task in tasks:
        chain_proposals = task.result()
        proposals.extend(chain_proposals)

    # Append error entries for chains where API query failed
    chains_with_errors = set(chain["displayname"] for chain in config["chains"]) - set(proposal[0] for proposal in proposals)
    for chain_name in chains_with_errors:
        proposals.append([
            chain_name,
            next(chain["chain-id"] for chain in config["chains"] if chain["displayname"] == chain_name),
            0,
            "ERR",
            "ERR",
            "ERR",
            0,
            0
        ])

    # Extract chain names and chain IDs for filter options
    chain_names = set()
    chain_ids = set()
    for chain in proposals:
        chain_names.add(chain[0])  # Chain Name
        chain_ids.add(chain[1])  # Chain ID

    # Delay the response to simulate data retrieval time
    time.sleep(2)

    # Render the index template with the collected proposals
    return render_template("index.html", proposals=proposals, chain_names=chain_names, chain_ids=chain_ids)


if __name__ == '__main__':
    app.run(debug=True)
