import pandas as pd
import asyncio
import httpx
import re
import logging
import os
from typing import List, Set

class EmailScraper:
    def __init__(self):
        self.setup_logging()
        self.seen_emails: Set[str] = set()  # Store lowercase emails for comparison

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def normalize_email(self, email: str) -> str:
        """Normalize email by converting to lowercase for comparison"""
        return email.lower().strip()

    def is_unique_email(self, email: str) -> bool:
        """Check if email is unique (case-insensitive)"""
        normalized = self.normalize_email(email)
        if normalized in self.seen_emails:
            return False
        self.seen_emails.add(normalized)
        return True

    def process_emails(self, emails: List[str]) -> List[str]:
        """Process and filter unique emails while preserving original case"""
        unique_emails = []
        for email in emails:
            if self.is_unique_email(email):
                unique_emails.append(email)  # Keep original case
        return unique_emails

    async def scrape_email_from_website(self, website: str) -> List[str]:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(website)
                response.raise_for_status()
                found_emails = re.findall(email_pattern, response.text)

                # Filter out invalid emails and process unique ones
                valid_emails = [
                    email for email in found_emails
                    if '.' in email.split('@')[1]
                    and not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                ]

                # Process unique emails
                emails = self.process_emails(valid_emails)

            except Exception as e:
                self.logger.error(f"Error scraping {website}: {e}")

        return emails

    async def process_websites(self, df: pd.DataFrame, output_file: str):
        results = []

        # Load existing emails if output file exists
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            if 'emails' in existing_df.columns:
                existing_emails = existing_df['emails'].dropna()
                for email_list in existing_emails:
                    if isinstance(email_list, str):
                        for email in email_list.split(', '):
                            self.seen_emails.add(self.normalize_email(email))

        for index, row in df.iterrows():
            if pd.notna(row['website']):
                self.logger.info(f"Processing {row['name']} - {row['website']}")
                emails = await self.scrape_email_from_website(row['website'])

                new_row = row.to_dict()
                new_row['emails'] = ', '.join(emails) if emails else 'N/A'
                results.append(new_row)

                self.logger.info(f"Found {len(emails)} unique emails for {row['name']}")
                self.save_row_to_csv(new_row, output_file)

            await asyncio.sleep(1)

        # Final save
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)

    def save_row_to_csv(self, row: dict, output_file: str):
        row_df = pd.DataFrame([row])

        if not os.path.exists(output_file):
            row_df.to_csv(output_file, index=False)
        else:
            row_df.to_csv(output_file, mode='a', header=False, index=False)

async def main():
    input_file = input("Enter the path to the CSV file (or press Enter to use default 'gmaps_data.csv'): ").strip()
    if not input_file:
        input_file = 'gmaps_data.csv'

    output_file = 'gmaps_data_with_emails.csv'

    try:
        df = pd.read_csv(input_file)
        df_with_websites = df[df['website'].notna()].copy()

        print(f"Found {len(df_with_websites)} entries with websites to process")

        scraper = EmailScraper()
        await scraper.process_websites(df_with_websites, output_file)

        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())