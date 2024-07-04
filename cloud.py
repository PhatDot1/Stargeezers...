import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Existing imports and function definitions...

def main():
    try:
        airtable_api_key = os.environ['AIRTABLE_API_KEY']
        base_id = 'appKI3FL67UBkEnGP'
        source_table_name = 'tbloH1PF4n2nxUtja'
        target_table_name = 'tblXFCGdFJMObMewK'

        with open('github_api_keys.txt', 'r') as f:
            api_keys = f.read().split(',')

        github_api_handler = GitHubApiHandler(api_keys)

        logger.info("Fetching records from Airtable...")
        records = get_airtable_records(airtable_api_key, base_id, source_table_name)
        logger.info(f"Fetched {len(records)} records from Airtable.")

        for record in records:
            fields = record.get('fields', {})
            github_url = fields.get('GitHub', '')
            status = fields.get('Status', '')

            logger.info(f"Record ID: {record['id']}, GitHub URL: {github_url}, Status: {status}")

            if github_url and status == 'Run C':
                logger.info(f"Setting record {record['id']} to 'Running'")
                update_airtable_record(airtable_api_key, base_id, source_table_name, record['id'], {'Status': 'Running'})

                logger.info(f"Processing record: {record['id']} with GitHub URL: {github_url}")
                try:
                    email = github_api_handler.get_user_info_from_github_api(github_url)
                    update_fields = {
                        'Scouted Email': email if email else '',
                        'Status': 'Done'
                    }
                    logger.info(f"Updating record {record['id']} with email: {update_fields['Scouted Email']}")
                    update_airtable_record(airtable_api_key, base_id, source_table_name, record['id'], update_fields)

                    if email:
                        new_record = {
                            'fields': {
                                'Name': fields.get('Name', ''),
                                'Github': github_url,
                                'Scouted Email': email,
                                'Repo to link': fields.get('Repo to Link', ''),
                                'Check External Hacker Github': 'Update (Github Repo)'
                            }
                        }
                        logger.info(f"Creating new record in target table with email: {email}")
                        create_airtable_records(airtable_api_key, base_id, target_table_name, [new_record])
                except Exception as e:
                    logger.error(f"An error occurred while processing {github_url}: {e}")
                    update_airtable_record(airtable_api_key, base_id, source_table_name, record['id'], {'Status': 'Error'})

    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()
