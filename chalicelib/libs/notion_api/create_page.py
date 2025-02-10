import os

from dotenv import load_dotenv
from loguru import logger
from notion_client import Client

load_dotenv()


def add_page_to_notion_database(
    content: str,
    company_name: str,
    person_name: str | None = None,
    chunk_size: int = 1900,
):
    text_chunks = []
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    for chunk in chunks:
        text_chunks.append(
            {
                "type": "text",
                "text": {
                    "content": chunk
                }
            }
        )

    client = Client(auth=os.getenv("NOTION_API_KEY"))
    response = client.pages.create(
        **{
            "parent": { "database_id": os.getenv("NOTION_DATABASE_ID") },
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": company_name
                            }
                        }
                    ]
                },
            },
            "children": [
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "caption": [],
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"企業名: {company_name}\n担当者: {person_name}",
                                    "link": None
                                },
                            }
                        ],
                        "language": "markdown"
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": text_chunks
                    }
                }
            ]
        }
    )
    logger.info(response)
    return response
